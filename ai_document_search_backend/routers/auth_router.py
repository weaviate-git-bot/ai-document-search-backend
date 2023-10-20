from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.auth_service import AuthService, Token

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post("/token")
@inject
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> Token:
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_access_token(data={"sub": user.username})
