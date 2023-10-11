import pandas as pd
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from pydantic import BaseModel

from ai_document_search_backend.database_providers.conversation_database import (
    Conversation,
    Message,
    Source,
)
from ai_document_search_backend.services.base_service import BaseService
from ai_document_search_backend.services.conversation_service import ConversationService

Exchange = tuple[str, str]


class ChatbotAnswer(BaseModel):
    text: str
    sources: list[Source]


class ChatbotService(BaseService):
    def __init__(
        self,
        *,
        conversation_service: ConversationService,
        weaviate_url: str,
        weaviate_api_key: str,
        openai_api_key: str,
        verbose: bool = False,
        temperature: float = 0,
    ):
        self.conversation_service = conversation_service
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(weaviate_api_key),
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.openai_api_key = openai_api_key
        self.verbose = verbose
        self.temperature = temperature

        self.weaviate_class_name = "UnstructuredDocument"
        self.custom_metadata_properties = ["isin", "shortname", "link"]

        super().__init__()

    def store(self, pdf_dir_path: str, metadata_path: str) -> None:
        """Store the documents in the vectorstore"""

        self.logger.info("Loading PDFs")
        loader = PyPDFDirectoryLoader(pdf_dir_path)
        data_pypdf = loader.load()
        df = pd.read_csv(metadata_path)
        for doc in data_pypdf:
            filename = doc.metadata["source"].split("/")[-1]
            metadata_row = df[df["filename"] == filename]
            for prop in self.custom_metadata_properties:
                doc.metadata[prop] = metadata_row[prop].values[0]

        self.logger.info(f"Storing {len(data_pypdf)} documents in Weaviate")
        Weaviate.from_documents(
            documents=data_pypdf,
            client=self.client,
            index_name=self.weaviate_class_name,
            by_text=False,
            embedding=self.embeddings,
        )

    def answer(self, question: str, username: str) -> ChatbotAnswer:
        """Answer the question"""

        vectorstore = Weaviate(
            self.client,
            index_name=self.weaviate_class_name,
            by_text=False,
            embedding=self.embeddings,
            text_key="text",
            attributes=self.custom_metadata_properties + ["page"],
        )
        llm = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=self.temperature)
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            verbose=self.verbose,
            return_source_documents=True,
        )

        conversation = self.conversation_service.get_latest_conversation(username)
        chat_history = self.__conversation_to_chat_history(conversation)

        self.logger.info(f"Answering question: {question}")
        result = qa({"question": question, "chat_history": chat_history})
        answer_text = result["answer"]
        self.logger.info(f"Answer: {answer_text}")
        sources = [
            Source(
                isin=source.metadata["isin"],
                shortname=source.metadata["shortname"],
                link=source.metadata["link"],
                page=source.metadata["page"],
            )
            for source in result["source_documents"]
        ]

        user_message = Message(role="user", text=question)
        assistant_message = Message(role="assistant", text=answer_text, sources=sources)
        self.conversation_service.add_to_latest_conversation(username, user_message)
        self.conversation_service.add_to_latest_conversation(username, assistant_message)

        return ChatbotAnswer(text=answer_text, sources=sources)

    def delete_schema(self) -> None:
        """Delete the schema"""

        self.client.schema.delete_all()

    @staticmethod
    def __conversation_to_chat_history(conversation: Conversation) -> list[Exchange]:
        """
        Convert a conversation to a chat history.
        Assumes that conversation messages are ordered by time and that the odd messages are from the user
        and the even messages are from the assistant.

        Exchange is a tuple of (question, answer)
        """

        return [
            (conversation.messages[i].text, conversation.messages[i + 1].text)
            for i in range(0, len(conversation.messages), 2)
        ]
