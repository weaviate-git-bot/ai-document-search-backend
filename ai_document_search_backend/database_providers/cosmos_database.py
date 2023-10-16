from datetime import datetime
import uuid
from typing import Optional

from azure.cosmos import CosmosClient


from ai_document_search_backend.database_providers.conversation_database import (
    ConversationDatabase,
    Conversation,
    Message,
)


class CosmosDBConversationDatabase(ConversationDatabase):
    def __init__(self, endpoint: str, key: str, db_name: str):
        self.client = CosmosClient(url=endpoint, credential=key)
        self.database = self.client.get_database_client(db_name)
        self.conversations = self.database.get_container_client("Conversations")

        super().__init__()

    def get_latest_conversation(self, username: str) -> Optional[Conversation]:
        query = "SELECT c.created_at, c.messages FROM conversation c WHERE c.user = @username ORDER BY c.created_at DESC"
        params = [dict(name="@username", value=username)]

        # If there is no conversation, create one
        try:
            latest_conversation = self.conversations.query_items(
                query=query, parameters=params, enable_cross_partition_query=False
            ).next()
            return latest_conversation
        except StopIteration:
            conversation = Conversation(created_at=self.__get_current_time(), messages=[])
            self.add_conversation(username, conversation)
            latest_conversation = self.conversations.query_items(
                query=query, parameters=params, enable_cross_partition_query=False
            ).next()
            return latest_conversation

    def add_conversation(self, username: str, conversation: Conversation) -> None:
        new_conversation = {
            "id": str(uuid.uuid4()),
            "user": username,
            "created_at": conversation.created_at,
            "messages": conversation.messages,
        }
        self.conversations.create_item(new_conversation)

    def add_to_latest_conversation(self, username: str, message: Message) -> None:
        QUERY = "SELECT * FROM conversation c WHERE c.user = @username ORDER BY c.created_at DESC"
        params = [dict(name="@username", value=username)]

        latest_conversation = self.conversations.query_items(
            query=QUERY, parameters=params, enable_cross_partition_query=False
        ).next()

        message_dict = {
            "role": message.role,
            "text": message.text,
        }

        if message.sources:
            sources_list = []

            for source in message.sources:
                source_dict = {
                    "isin": source.isin,
                    "shortname": source.shortname,
                    "link": source.link,
                    "page": source.page,
                }
                sources_list.append(source_dict)

            message_dict["sources"] = sources_list

        latest_conversation["messages"].append(message_dict)

        new_conversation = {
            "id": latest_conversation["id"],
            "user": latest_conversation["user"],
            "created_at": latest_conversation["created_at"],
            "messages": latest_conversation["messages"],
        }

        self.conversations.replace_item(latest_conversation["id"], new_conversation)

    def clear_conversations(self, username: str) -> None:
        # Can only be used if we enable the delete items by partition key feature, which requires a paid account
        # self.conversations.delete_all_items_by_partition_key(username)

        QUERY = "SELECT * FROM conversation c WHERE c.user = @username ORDER BY c.created_at DESC"
        params = [dict(name="@username", value=username)]
        conversations = self.conversations.query_items(
            query=QUERY, parameters=params, enable_cross_partition_query=False
        )
        for conversation in conversations:
            conversation_id = conversation["id"]
            self.conversations.delete_item(item=conversation_id, partition_key=username)

    @staticmethod
    def __get_current_time() -> str:
        return datetime.now().isoformat()
