from ai_document_search_backend.database_providers.conversation_database import (
    Conversation,
    Message,
    Source,
)
from ai_document_search_backend.utils.conversation_to_chat_history import (
    conversation_to_chat_history,
)

user_message = Message(is_from_bot=False, text="Hello")
bot_message = Message(
    is_from_bot=True,
    text="Hi",
    sources=[
        Source(
            isin="NO1111111111",
            shortname="Bond 2021",
            link="https://www.example.com/bond1.pdf",
            page=1,
            certainty=0.9,
            distance=0.1,
        ),
        Source(
            isin="NO2222222222",
            shortname="Bond 2022",
            link="https://www.example.com/bond2.pdf",
            page=5,
            certainty=0.8,
            distance=0.2,
        ),
    ],
)


def test_conversation_to_chat_history():
    conversation = Conversation(
        created_at="2021-01-01T00:00:00", messages=[user_message, bot_message]
    )
    chat_history = conversation_to_chat_history(conversation)
    assert chat_history == [("Hello", "Hi")]
