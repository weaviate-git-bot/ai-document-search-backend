from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ai_document_search_backend.services.base_service import BaseService


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


class AuthService(BaseService):

    def __init__(self, algorithm: str, access_token_expire_minutes: int, secret_key: str, username: str, password: str) -> None:
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.secret_key = secret_key

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.users_db = {
            username: {
                "username": username,
                "hashed_password": self.__get_password_hash(password),
            }
        }

        super().__init__()

    def authenticate_user(self, username: str, password: str) -> Union[Optional[UserInDB], bool]:
        user = self.__get_user(username)
        if not user:
            return False
        if not self.__verify_password(password, user.hashed_password):
            return False
        self.logger.debug(
            "User %s has been successfully authenticated",
            user.username,
        )
        return user

    def create_access_token(self, data: dict) -> Token:
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return Token(access_token=encoded_jwt, token_type="bearer")

    def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = self.__get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    def __get_user(self, username: str) -> Optional[UserInDB]:
        db = self.users_db
        if username in db:
            user_dict = db[username]
            return UserInDB(**user_dict)

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def __get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
