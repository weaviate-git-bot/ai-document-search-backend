from typing import Optional, Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from .containers import Container
from .services import SummarizationService


class SummarizationResponse(BaseModel):
    summary: str
    


class User(BaseModel):
    username: str
    email: str 
    full_name: str 
    disabled: bool 
    
class UserInDB(User):
    password: str
    
fake_users_db = {
    "marius": {
        "username": "marius",
        "full_name": "Marius Berdal Gaalaas",
        "email": "marius@gmail.com",
        "password": "123",
        "disabled": False,
    }
}

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

# def fake_decode_token(token):
#     return User(
#         username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
#     )


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user


# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

@router.get("/")
@router.get("/health")
async def health():
    return "OK"

#For authenticating
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username) #TODO: Make proper users
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password = form_data.password
    if not password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/summarization")
@inject
def summarization(
    text: str,
    summary_length: Optional[int] = None,
    default_summary_length: int = Depends(Provide[Container.config.default.summary_length]),
    summarization_service: SummarizationService = Depends(Provide[Container.summarization_service]),
) -> SummarizationResponse:
    summary_length = summary_length or default_summary_length

    summary = summarization_service.summarize(text, summary_length)

    return SummarizationResponse(summary=summary)
