import pandas as pd
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from pydantic import BaseModel

from ai_document_search_backend.services.base_service import BaseService
from ai_document_search_backend.services.chat_history_service import ChatHistoryService


class Source(BaseModel):
    isin: str
    link: str
    page: int


class ChatbotAnswer(BaseModel):
    text: str
    sources: list[Source]


class ChatbotService(BaseService):
    def __init__(
        self,
        *,
        chat_history_service: ChatHistoryService,
        weaviate_url: str,
        weaviate_api_key: str,
        openai_api_key: str,
        verbose: bool = False,
        temperature: float = 0,
    ):
        self.chat_history_service = chat_history_service
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(weaviate_api_key),
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.openai_api_key = openai_api_key
        self.weaviate_class_name = "UnstructuredDocument"
        self.verbose = verbose
        self.temperature = temperature

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
            doc.metadata["isin"] = metadata_row["isin"].values[0]
            doc.metadata["link"] = metadata_row["link"].values[0]

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
            attributes=["isin", "link", "page"],
        )
        llm = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=self.temperature)
        # memory = ConversationSummaryMemory(
        #     llm=llm,
        #     memory_key="chat_history",
        #     output_key="answer",
        #     return_messages=True,
        # )
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            # memory=memory,
            verbose=self.verbose,
            return_source_documents=True,
        )

        chat_history = self.chat_history_service.get_chat_history(username)

        self.logger.info(f"Answering question: {question}")
        result = qa({"question": question, "chat_history": chat_history})
        answer_text = result["answer"]
        self.logger.info(f"Answer: {answer_text}")
        sources = [
            Source(
                isin=source.metadata["isin"],
                link=source.metadata["link"],
                page=source.metadata["page"],
            )
            for source in result["source_documents"]
        ]

        self.chat_history_service.add_chat_history(username, question, answer_text)

        return ChatbotAnswer(text=answer_text, sources=sources)

    def delete_schema(self) -> None:
        """Delete the schema"""

        self.client.schema.delete_all()
