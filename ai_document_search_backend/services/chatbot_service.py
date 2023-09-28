from dotenv import load_dotenv

from langchain.llms import OpenAI

from ai_document_search_backend.services.base_service import BaseService

load_dotenv()

llm = OpenAI()


class ChatbotService(BaseService):
    def answer(self, question: str) -> str:
        """Answer the question"""
        answer = llm.predict(question)
        return answer.strip()
        #return question
