from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from .config import Settings

SECRETKEY = Settings().secretkey
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool


class UserInDB(User):
    hashed_password: str


class Salt(BaseModel):
    username: str
    salt: str


class SaltInDB(Salt):
    salt: str


fake_users_db = {
    "marius": {
        "username": "marius",
        "full_name": "Marius Berdal Gaalaas",
        "email": "marius@gmail.com",
        "hashed_password": "$2b$12$SXT6OzyrQxVZLjW1QAawMe5qUORtJ6RHy1w3cE86U1aV0lc3NDG7S",
        "disabled": False,
    },
    "test": {
        "username": "test",
        "full_name": "Test Testesen",
        "email": "test@gmail.com",
        "hashed_password": "$2b$12$jWutkf9LKP9qxQBKwnIjNetU13STTvuZaoBIqmcfCk9pBpZyg1Jey",
        "disabled": False,
    },
}

fake_salts_db = {
    "marius": {"username": "marius", "salt": "fNRmPKbYOeHEYDor22GcZMN8tSeAT4Ac"},
    "test": {"username": "test", "salt": "DWs93J1MgEOKQ0Tz0pxgtsnM4I4VNSDz"},
}

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_hashed_password(password: str):
    return password_context.hash(password)


def check_password(password: str, hashed_password: str):
    return password_context.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    data_copy = data.copy()
    expire_time = datetime.utcnow() + expires_delta
    data_copy.update({"exp": expire_time})
    token = jwt.encode(data_copy, SECRETKEY, algorithm=ALGORITHM)
    return token


# For authenticating
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)  # TODO: Make proper users
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    salt = fake_salts_db.get(form_data.username)["salt"]
    password = form_data.password
    if not check_password(salt + password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=token_expires)

    return {"access_token": token, "token_type": "bearer"}


# Call to validate a token
@router.get("/validate_token")
async def main(token: Annotated[str, Depends(oauth2_scheme)]):
    username = ""
    try:
        payload = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if username == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "Token Validated"
