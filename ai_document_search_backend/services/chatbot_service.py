from pathlib import Path

import pandas as pd
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
from pydantic import BaseModel

from ai_document_search_backend.database_providers.conversation_database import (
    Source,
)
from ai_document_search_backend.services.base_service import BaseService

Exchange = tuple[str, str]


class ChatbotAnswer(BaseModel):
    text: str
    sources: list[Source]


class ChatbotService(BaseService):
    def __init__(
        self,
        *,
        weaviate_client: weaviate.Client,
        openai_api_key: str,
        embedding_model: str,
        question_answering_model: str,
        condense_question_model: str,
        verbose: bool = False,
        temperature: float = 0,
    ):
        self.client = weaviate_client
        self.question_answering_model = question_answering_model
        self.condense_question_model = condense_question_model
        self.embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=openai_api_key)
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
            filename = Path(doc.metadata["source"]).name
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

    def answer(self, question: str, chat_history: list[Exchange]) -> ChatbotAnswer:
        """Answer the question"""

        vectorstore = Weaviate(
            self.client,
            index_name=self.weaviate_class_name,
            by_text=False,
            embedding=self.embeddings,
            text_key="text",
            attributes=self.custom_metadata_properties + ["page"],
        )
        question_answering_llm = ChatOpenAI(
            model=self.question_answering_model,
            openai_api_key=self.openai_api_key,
            temperature=self.temperature,
        )
        condense_question_llm = ChatOpenAI(
            model=self.condense_question_model,
            openai_api_key=self.openai_api_key,
            temperature=self.temperature,
        )
        qa = ConversationalRetrievalChain.from_llm(
            llm=question_answering_llm,
            retriever=vectorstore.as_retriever(
                search_kwargs={"additional": ["certainty", "distance"], "k": 4}
            ),
            verbose=self.verbose,
            return_source_documents=True,
            condense_question_llm=condense_question_llm,
        )

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
                certainty=round(source.metadata["_additional"]["certainty"], 3),
                distance=round(source.metadata["_additional"]["distance"], 3),
            )
            for source in result["source_documents"]
        ]

        return ChatbotAnswer(text=answer_text, sources=sources)

    def delete_schema(self) -> None:
        """Delete the schema"""

        self.client.schema.delete_all()
