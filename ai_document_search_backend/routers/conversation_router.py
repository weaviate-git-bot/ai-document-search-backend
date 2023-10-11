from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.auth_service import AuthService
from ai_document_search_backend.services.conversation_service import Conversation, ConversationService

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.get("/")
@inject
async def get_latest_conversation(
        token: Annotated[str, Depends(oauth2_scheme)],
        auth_service: AuthService = Depends(Provide[Container.auth_service]),
        conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> Conversation:
    user = auth_service.get_current_user(token)
    return conversation_service.get_latest_conversation(user.username)


@router.post("/")
@inject
async def create_new_conversation(
        token: Annotated[str, Depends(oauth2_scheme)],
        auth_service: AuthService = Depends(Provide[Container.auth_service]),
        conversation_service: ConversationService = Depends(Provide[Container.conversation_service]),
) -> Conversation:
    user = auth_service.get_current_user(token)
    return conversation_service.create_new_conversation(user.username)
