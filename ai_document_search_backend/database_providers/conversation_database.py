from abc import ABC, abstractmethod
from typing import Union, Literal, Optional
import json

from pydantic import BaseModel


class Source(BaseModel):
    isin: str
    shortname: str
    link: str
    page: int


class Message(BaseModel):
    role: Union[Literal["user"], Literal["assistant"]]
    text: str
    sources: Optional[list[Source]] = None
    
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Conversation(BaseModel):
    created_at: str
    messages: list[Message]


class ConversationDatabase(ABC):
    @abstractmethod
    def get_latest_conversation(self, username: str) -> Optional[Conversation]:
        raise NotImplementedError

    @abstractmethod
    def add_conversation(self, username: str, conversation: Conversation) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_to_latest_conversation(self, username: str, message: Message) -> None:
        raise NotImplementedError
