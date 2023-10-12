from typing import Optional

from ai_document_search_backend.database_providers.conversation_database import (
    ConversationDatabase,
    Conversation,
    Message,
)


class InMemoryConversationDatabase(ConversationDatabase):
    def __init__(self):
        self.db: dict[str, list[Conversation]] = {}

        super().__init__()

    def get_latest_conversation(self, username: str) -> Optional[Conversation]:
        return self.db.get(username, [None])[-1]

    def add_conversation(self, username: str, conversation: Conversation) -> None:
        self.db.setdefault(username, []).append(conversation)

    def add_to_latest_conversation(self, username: str, message: Message) -> None:
        latest_conversation = self.get_latest_conversation(username)
        if latest_conversation is None:
            raise ValueError(f"No conversation found for user {username}")
        latest_conversation.messages.append(message)
