from abc import ABC, abstractmethod
from typing import Optional, Literal

from pydantic import BaseModel


class Source(BaseModel):
    isin: str
    shortname: str
    link: str
    page: int
    certainty: float
    distance: float


class Message(BaseModel):
    role: Literal["user", "bot"]
    text: str
    sources: Optional[list[Source]] = None


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
    def add_to_latest_conversation(
        self, username: str, user_message: Message, bot_message: Message
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear_conversations(self, username: str) -> None:
        raise NotImplementedError
