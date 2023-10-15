import uuid
from yaml import load, dump
from typing import Optional

from azure.cosmos import CosmosClient, PartitionKey


from ai_document_search_backend.database_providers.conversation_database import (
    ConversationDatabase,
    Conversation,
    Message,
)

class CosmosDBConversationDatabase(ConversationDatabase):
    def __init__(self, endpoint: str, key:str, db_name:str):
        self.client = CosmosClient(url=endpoint, credential=key)
        self.database = self.client.get_database_client(db_name)
        self.conversations = self.database.get_container_client("Conversations")

        super().__init__()

    def get_latest_conversation(self, username: str) -> Optional[Conversation]:
        QUERY = "SELECT c.created_at, c.messages FROM conversation c WHERE c.user = @username ORDER BY c.created_at DESC"
        params = [dict(name='@username', value=username)]
        
        
        latest_conversation = self.conversations.query_items(query=QUERY, parameters=params, enable_cross_partition_query=False).next()
        print("Convo\n")
        print(latest_conversation)
        print("\n\n\nDecode")
        # print(jsonpickle.decode(latest_conversation))
        
        return latest_conversation
        
    def add_conversation(self, username: str, conversation: Conversation) -> None:
        new_conversation = {
            "id": str(uuid.uuid4()),
            "user": username,
            "created_at": conversation.created_at,
            "messages": conversation.messages
        }
        self.conversations.create_item(new_conversation)


    def add_to_latest_conversation(self, username: str, message: Message) -> None:
        QUERY = "SELECT * FROM conversation c WHERE c.user = @username ORDER BY c.created_at DESC"
        params = [dict(name='@username', value=username)]
        
        
        latest_conversation = self.conversations.query_items(query=QUERY, parameters=params, enable_cross_partition_query=False).next()

        message_dict = {
            'role': message.role,
            'text': message.text,
        }

        if message.sources:

            sources_list = []

            for source in message.sources:
                source_dict = {
                    'isin': source.isin,
                    'shortname': source.shortname,
                    'link': source.link,
                    'page': source.page
                }
                sources_list.append(source_dict)

            message_dict['sources'] = sources_list

        
        latest_conversation['messages'].append(message_dict)
        
        new_conversation = {
            "id": latest_conversation['id'],
            "user": latest_conversation['user'],
            "created_at": latest_conversation['created_at'],
            "messages": latest_conversation['messages']
        }
        
        self.conversations.replace_item(latest_conversation['id'], new_conversation)
        
        # raise NotImplementedError
