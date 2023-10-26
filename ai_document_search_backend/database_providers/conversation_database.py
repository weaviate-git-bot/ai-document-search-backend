from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class Source(BaseModel):
    isin: str
    shortname: str
    link: str
    page: int
    certainty: float
    distance: float


class Message(BaseModel):
    is_from_bot: bool
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
