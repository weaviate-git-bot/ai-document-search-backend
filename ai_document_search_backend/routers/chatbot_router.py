from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.database_providers.conversation_database import Message
from ai_document_search_backend.services.chatbot_service import (
    ChatbotService,
    ChatbotAnswer,
)
from ai_document_search_backend.services.auth_service import AuthService
from ai_document_search_backend.services.conversation_service import ConversationService
from ai_document_search_backend.utils.conversation_to_chat_history import (
    conversation_to_chat_history,
)


router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class ChatbotRequest(BaseModel):
    question: str


@router.post("/")
@inject
async def answer_question(
    request: ChatbotRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service]),
    conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> ChatbotAnswer:
    username = auth_service.get_current_user(token).username

    conversation = conversation_service.get_latest_conversation(username)
    chat_history = conversation_to_chat_history(conversation)

    question = request.question
    answer = chatbot_service.answer(question, chat_history)

    conversation_service.add_to_latest_conversation(
        username, Message(origin_bot=False, text=question)
    )
    conversation_service.add_to_latest_conversation(
        username, Message(origin_bot=True, text=answer.text, sources=answer.sources)
    )

    return ChatbotAnswer(text=answer.text, sources=answer.sources)
