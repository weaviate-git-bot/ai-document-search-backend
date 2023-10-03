import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain.vectorstores import Weaviate
from pydantic import BaseModel

from ai_document_search_backend.services.base_service import BaseService


class ChatbotAnswer(BaseModel):
    text: str


class ChatbotService(BaseService):
    def __init__(
        self,
        *,
        weaviate_url: str,
        weaviate_api_key: str,
        openai_api_key: str,
        verbose: bool = False,
        temperature: float = 0,
    ):
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

    def store(self, pdf_dir_path: str) -> None:
        """Store the documents in the vectorstore"""
        self.logger.info("Loading PDFs")
        loader = PyPDFDirectoryLoader(pdf_dir_path)
        data_pypdf = loader.load()

        self.logger.info(f"Storing {len(data_pypdf)} documents in Weaviate")
        Weaviate.from_documents(
            documents=data_pypdf,
            client=self.client,
            index_name=self.weaviate_class_name,
            by_text=False,
            embedding=self.embeddings,
        )

    def answer(self, question: str) -> ChatbotAnswer:
        """Answer the question"""
        vectorstore = Weaviate(
            self.client,
            index_name=self.weaviate_class_name,
            by_text=False,
            embedding=self.embeddings,
            text_key="text",
        )
        llm = ChatOpenAI(
            openai_api_key=self.openai_api_key, temperature=self.temperature
        )
        memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
        )
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory,
            verbose=self.verbose,
            return_source_documents=True,
        )

        self.logger.info(f"Answering question: {question}")
        answer_text = qa(question)["answer"]
        self.logger.info(f"Answer: {answer_text}")
        return ChatbotAnswer(text=answer_text)
