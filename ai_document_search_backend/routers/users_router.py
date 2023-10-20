from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.auth_service import AuthService, User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.get("/me")
@inject
def read_users_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> User:
    return auth_service.get_current_user(token)
