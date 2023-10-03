from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.chatbot_service import (
    ChatbotService,
    ChatbotAnswer,
)
from ai_document_search_backend.services.auth_service import AuthService


router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class ChatbotResponse(BaseModel):
    answer: ChatbotAnswer


class ChatbotRequest(BaseModel):
    question: str


@router.post("/")
@inject
async def question(
    request: ChatbotRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service]),
) -> ChatbotResponse:
    auth_service.get_current_user(token)
    answer = chatbot_service.answer(request.question)
    return ChatbotResponse(answer=answer)
