from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.chatbot_service import ChatbotService


router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatbotResponse(BaseModel):
    answer: str


class ChatbotRequest(BaseModel):
    question: str


@router.get("/")
@inject
async def question(
    request: ChatbotRequest,
    chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service]),
) -> ChatbotResponse:
    answer = chatbot_service.answer(request.question)
    return ChatbotResponse(answer=answer)
