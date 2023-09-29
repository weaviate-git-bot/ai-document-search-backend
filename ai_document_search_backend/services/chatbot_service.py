from dotenv import load_dotenv

from langchain.llms import OpenAI
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

from ai_document_search_backend.services.base_service import BaseService
from ai_document_search_backend.utils.relative_path_from_file import (
    relative_path_from_file,
)


load_dotenv()

PDF_DIR_PATH = relative_path_from_file(__file__, "../../data/")

# Load PDF
loader = PyPDFDirectoryLoader(PDF_DIR_PATH)
data = loader.load()

# Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=0
)  # Context-aware splitters keep the location ("context") of each split in the original Document - useful for later
all_splits = text_splitter.split_documents(data)

# Store in vectorstore - chroma stores locally
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())


# Generate
llm = OpenAI()


class ChatbotService(BaseService):
    def answer(self, question: str) -> str:
        """Answer the question"""
        docs = vectorstore.similarity_search(question)
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())
        text = qa_chain({"query": question})["result"]
        return text.strip()
        # return question
