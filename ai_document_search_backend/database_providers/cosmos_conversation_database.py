import uuid
from typing import Optional

from azure.cosmos import CosmosClient, PartitionKey
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ai_document_search_backend.database_providers.conversation_database import (
    ConversationDatabase,
    Conversation,
    Message,
)


class DBConversation(BaseModel):
    id: str
    username: str
    created_at: str
    messages: list[Message]


class CosmosConversationDatabase(ConversationDatabase):
    def __init__(self, url: str, key: str, db_name: str, offer_throughput: int):
        self.client = CosmosClient(url=url, credential=key)
        self.database = self.client.create_database_if_not_exists(id=db_name)
        self.conversations = self.database.create_container_if_not_exists(
            id="Conversations",
            partition_key=PartitionKey(path="/username"),
            offer_throughput=offer_throughput,
        )

        super().__init__()

    def get_latest_conversation(self, username: str) -> Optional[Conversation]:
        db_conversation = self.__get_latest_db_conversation(username)
        if db_conversation is None:
            return None
        return Conversation(
            created_at=db_conversation["created_at"], messages=db_conversation["messages"]
        )

    def add_conversation(self, username: str, conversation: Conversation) -> None:
        new_conversation = {
            "id": str(uuid.uuid4()),
            "username": username,
            "created_at": conversation.created_at,
            "messages": jsonable_encoder(conversation.messages),
        }
        self.conversations.create_item(new_conversation)

    def add_to_latest_conversation(
        self, username: str, user_message: Message, bot_message: Message
    ) -> None:
        db_conversation = self.__get_latest_db_conversation(username)
        if db_conversation is None:
            raise ValueError(f"No conversation found for user {username}")

        db_conversation["messages"].append(jsonable_encoder(user_message))
        db_conversation["messages"].append(jsonable_encoder(bot_message))

        self.conversations.replace_item(item=db_conversation["id"], body=db_conversation)

    def clear_conversations(self, username: str) -> None:
        query = "SELECT * FROM conversation c WHERE c.username = @username"
        params = [dict(name="@username", value=username)]
        conversations = self.conversations.query_items(
            query=query, parameters=params, enable_cross_partition_query=False
        )
        for conversation in conversations:
            conversation_id = conversation["id"]
            self.conversations.delete_item(item=conversation_id, partition_key=username)

    def __get_latest_db_conversation(self, username: str) -> Optional[DBConversation]:
        query = "SELECT * FROM conversation c WHERE c.username = @username ORDER BY c.created_at DESC OFFSET 0 LIMIT 1"
        params = [dict(name="@username", value=username)]

        db_conversations = self.conversations.query_items(
            query=query, parameters=params, enable_cross_partition_query=False
        )
        return next(db_conversations, None)
