from pathlib import Path

import pandas as pd
import weaviate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.vectorstores import Weaviate
from pydantic import BaseModel

from ai_document_search_backend.database_providers.conversation_database import (
    Source,
)
from ai_document_search_backend.services.base_service import BaseService
from ai_document_search_backend.utils.filters import construct_and_filter, Filter

Exchange = tuple[str, str]


class ChatbotAnswer(BaseModel):
    text: str
    sources: list[Source]


class Filters(BaseModel):
    isin: list[str]
    issuer_name: list[str]
    filename: list[str]
    industry: list[str]
    risk_type: list[str]
    green: list[str]


class ChatbotException(Exception):
    def __init__(self, message: str):
        self.message = message


class ChatbotService(BaseService):
    def __init__(
        self,
        *,
        weaviate_client: weaviate.Client,
        openai_api_key: str,
        question_answering_model: str,
        condense_question_model: str,
        weaviate_class_name: str,
        num_sources: int = 4,
        verbose: bool = False,
        temperature: float = 0,
    ):
        self.client = weaviate_client
        self.question_answering_model = question_answering_model
        self.condense_question_model = condense_question_model
        self.openai_api_key = openai_api_key
        self.weaviate_class_name = weaviate_class_name
        self.num_sources = num_sources
        self.verbose = verbose
        self.temperature = temperature

        self.text_key = "text"
        self.custom_metadata_properties = [
            "link",
            "shortname",
            "isin",
            "issuer_name",
            "filename",
            "industry",
            "risk_type",
            "green",
        ]

        super().__init__()

    def store(self, pdf_dir_path: str, metadata_path: str) -> None:
        """Store the documents in the vectorstore"""

        self.logger.info("Loading PDFs")
        loader = PyPDFDirectoryLoader(pdf_dir_path)
        documents = loader.load()
        if len(documents) == 0:
            raise ValueError(f"No PDFs found in {pdf_dir_path}")

        df = pd.read_csv(metadata_path)
        pdf_page_objects = []
        for doc in documents:
            text = doc.page_content
            if text == "":
                continue
            pdf_page_object = {
                self.text_key: text,
                "page": doc.metadata["page"],
                "source": doc.metadata["source"],
            }
            filename = Path(doc.metadata["source"]).name
            metadata_row = df[df["filename"] == filename]
            for prop in self.custom_metadata_properties:
                pdf_page_object[prop] = metadata_row[prop].values[0]
            pdf_page_objects.append(pdf_page_object)

        self.logger.info(f"Storing {len(pdf_page_objects)} objects in Weaviate")

        if not self.client.schema.exists(self.weaviate_class_name):
            self.logger.info(f"Creating class {self.weaviate_class_name}")
            class_obj = {
                "class": self.weaviate_class_name,
                "properties": [
                    {
                        "name": self.text_key,
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": False,
                            }
                        },
                    },
                    {
                        "name": "page",
                        "dataType": ["number"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                            }
                        },
                    },
                    {
                        "name": "source",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                            }
                        },
                    },
                    {
                        "name": "link",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                            }
                        },
                    },
                    {
                        "name": "shortname",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "isin",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "issuer_name",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "filename",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "industry",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "risk_type",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                    {
                        "name": "green",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": True,
                            }
                        },
                    },
                ],
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text",
                        "vectorizeClassName": False,
                    },
                },
            }
            self.client.schema.create_class(class_obj)

        self.client.batch.configure(batch_size=100)
        with self.client.batch as batch:
            for pdf_page_object in pdf_page_objects:
                batch.add_data_object(
                    data_object=pdf_page_object,
                    class_name=self.weaviate_class_name,
                )

        self.logger.info(
            f"Number of {self.weaviate_class_name} objects in Weaviate: {self.__get_number_of_objects()}"
        )

    def answer(
        self, question: str, chat_history: list[Exchange], filters: list[Filter]
    ) -> ChatbotAnswer:
        """Answer the question"""

        vectorstore = Weaviate(
            self.client,
            index_name=self.weaviate_class_name,
            by_text=True,
            text_key=self.text_key,
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
                search_kwargs={
                    "additional": ["certainty", "distance"],
                    "k": self.num_sources,
                    "where_filter": construct_and_filter(filters),
                }
            ),
            condense_question_llm=condense_question_llm,
            return_source_documents=True,
            verbose=self.verbose,
        )

        self.logger.info(f"Answering question: {question}")
        try:
            result = qa({"question": question, "chat_history": chat_history})
        except Exception as e:
            self.logger.error(f"Error while answering question: {e}")
            raise ChatbotException(f"Error while answering question: {e}")
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

    def get_filters(self) -> Filters:
        return Filters(
            isin=self.__get_available_values("isin"),
            issuer_name=self.__get_available_values("issuer_name"),
            filename=self.__get_available_values("filename"),
            industry=self.__get_available_values("industry"),
            risk_type=self.__get_available_values("risk_type"),
            green=self.__get_available_values("green"),
        )

    def __get_number_of_objects(self) -> int:
        result = self.client.query.aggregate(self.weaviate_class_name).with_meta_count().do()
        number_of_objects = result["data"]["Aggregate"][self.weaviate_class_name][0]["meta"][
            "count"
        ]
        return number_of_objects

    def __get_available_values(self, property_name: str) -> list[str]:
        result = (
            self.client.query.aggregate(self.weaviate_class_name)
            .with_group_by_filter(property_name)
            .with_fields("groupedBy { path value }")
            .do()
        )
        available_values = [
            group["groupedBy"]["value"]
            for group in result["data"]["Aggregate"][self.weaviate_class_name]
        ]
        return available_values
