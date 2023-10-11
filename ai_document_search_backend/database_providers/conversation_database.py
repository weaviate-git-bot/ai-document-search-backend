from abc import ABC, abstractmethod
from typing import Union, Literal, Optional

from pydantic import BaseModel


class Source(BaseModel):
    isin: str
    link: str
    page: int


class Message(BaseModel):
    role: Union[Literal["user"], Literal["assistant"]]
    text: str
    sources: Optional[list[Source]] = None


class Conversation(BaseModel):
    createdAt: str
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
