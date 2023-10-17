from ai_document_search_backend.database_providers.conversation_database import Conversation
from ai_document_search_backend.services.chatbot_service import Exchange


def conversation_to_chat_history(conversation: Conversation) -> list[Exchange]:
    """
    Convert a conversation to a chat history.
    Assumes that conversation messages are ordered by time and that the odd messages are from the user
    and the even messages are from the assistant.

    Exchange is a tuple of (question, answer)
    """

    return [
        (conversation.messages[i].text, conversation.messages[i + 1].text)
        for i in range(0, len(conversation.messages), 2)
    ]
