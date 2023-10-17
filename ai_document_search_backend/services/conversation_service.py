from datetime import datetime

from ai_document_search_backend.database_providers.conversation_database import (
    Conversation,
    ConversationDatabase,
    Message,
)
from ai_document_search_backend.services.base_service import BaseService


class ConversationService(BaseService):
    def __init__(self, conversation_database: ConversationDatabase):
        self.conversation_database = conversation_database

        super().__init__()

    def get_latest_conversation(self, username: str) -> Conversation:
        conversation = self.conversation_database.get_latest_conversation(username)
        if conversation is None:
            conversation = self.create_new_conversation(username)
        return conversation

    def create_new_conversation(self, username: str) -> Conversation:
        new_conversation = Conversation(created_at=self.__get_current_time(), messages=[])
        self.conversation_database.add_conversation(username, new_conversation)
        return new_conversation

    def add_to_latest_conversation(self, username: str, message: Message) -> None:
        self.conversation_database.add_to_latest_conversation(username, message)

    def clear_conversations(self, username: str) -> str:
        self.conversation_database.clear_conversations(username)
        return f"Conversations deleted for user {username}"

    @staticmethod
    def __get_current_time() -> str:
        return datetime.now().isoformat()
