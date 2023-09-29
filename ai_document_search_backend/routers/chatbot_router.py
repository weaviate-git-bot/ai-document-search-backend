from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.chatbot_service import ChatbotService


router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatbotAnswer(BaseModel):
    text: str


class ChatbotResponse(BaseModel):
    answer: ChatbotAnswer


class ChatbotRequest(BaseModel):
    question: str


@router.post("/")
@inject
async def question(
    request: ChatbotRequest,
    chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service]),
) -> ChatbotResponse:
    text = chatbot_service.answer(request.question)
    answer = ChatbotAnswer(text=text)
    return ChatbotResponse(answer=answer)
