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
        all_conversations = self.db.get(username, [])
        if not all_conversations:
            return None
        return sorted(all_conversations, key=lambda x: x.created_at)[-1]

    def add_conversation(self, username: str, conversation: Conversation) -> None:
        self.db.setdefault(username, []).append(conversation)

    def add_to_latest_conversation(
        self, username: str, user_message: Message, bot_message: Message
    ) -> None:
        latest_conversation = self.get_latest_conversation(username)
        if latest_conversation is None:
            raise ValueError(f"No conversation found for user {username}")
        latest_conversation.messages.append(user_message)
        latest_conversation.messages.append(bot_message)

    def clear_conversations(self, username: str) -> None:
        self.db[username] = []
