import dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain.vectorstores import Weaviate

from ai_document_search_backend.utils.relative_path_from_file import relative_path_from_file

DATA_PATH = relative_path_from_file(__file__, "../../data/pdfs/NO0010914682_LA_20201217.PDF")
WEAVIATE_URL = 'http://localhost:8080'

# Load OPENAI_API_KEY
dotenv.load_dotenv()

# 1.+2. Load + Split
loader = PyPDFLoader(DATA_PATH)
pages = loader.load_and_split()

# 3. Store
# faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
# docs = faiss_index.similarity_search("How will the community be engaged?", k=2)
# for doc in docs:
#     print(str(doc.metadata["page"]) + ":", doc.page_content[:300])

vectorstore = Weaviate.from_documents(documents=pages, embedding=OpenAIEmbeddings(), weaviate_url=WEAVIATE_URL, by_text=False)

# 4. Retrieve
retriever = vectorstore.as_retriever()

# 5.+6. Generate + Chat
llm = ChatOpenAI()
memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory, verbose=False)

print(qa("What is the Loan to value ratio?")["answer"])
print(qa("How large is it?")["answer"])
