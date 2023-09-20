from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext


class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool


class UserInDB(User):
    hashedPassword: str


fake_users_db = {
    "marius": {
        "username": "marius",
        "full_name": "Marius Berdal Gaalaas",
        "email": "marius@gmail.com",
        "hashedPassword": "$2b$12$N.OxhYBrt0wuYllbXZCYFOd4olBwdFtaazpIJdwqmn2h9SVoKuhQq",
        "disabled": False,
    },
    "test": {
        "username": "test",
        "full_name": "Test Testesen",
        "email": "test@gmail.com",
        "hashedPassword": "$2b$12$NPWuQY.iiARfulUEzfEXcekunrbBlZF9Uvz.mACsTw0zfbHS.zJzq",
        "disabled": False,
    },
}

passwordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")


def hashedPassword(password):
    return passwordContext.hash(password)


def checkPassword(password, hashedPassword):
    return passwordContext.verify(password, hashedPassword)


# For authenticating
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)  # TODO: Make proper users
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password = form_data.password
    if not checkPassword(password, user.hashedPassword):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
