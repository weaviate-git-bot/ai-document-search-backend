from typing import Optional, Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from .containers import Container


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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# For authenticating
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)  # TODO: Make proper users
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password = form_data.password
    if not password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
