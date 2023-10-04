from abc import ABC, abstractmethod

from ai_document_search_backend.services.base_service import BaseService

Exchange = tuple[str, str]


class ChatHistoryService(ABC, BaseService):
    @abstractmethod
    def get_chat_history(self, username: str) -> list[Exchange]:
        raise NotImplementedError

    @abstractmethod
    def add_chat_history(self, username: str, question: str, answer: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_chat_history(self, username: str) -> None:
        raise NotImplementedError
