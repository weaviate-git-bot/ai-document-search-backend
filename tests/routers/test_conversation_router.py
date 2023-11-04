import pytest
from anys import ANY_STR
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app
from ai_document_search_backend.database_providers.conversation_database import (
    Message,
    Source,
    Conversation,
)

test_username = "test_user"
test_password = "test_password"

user_message = Message(role="user", text="Hello")
bot_message = Message(
    role="bot",
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

app.container.config.auth.secret_key.from_value("test_secret_key")
app.container.config.auth.username.from_value(test_username)
app.container.config.auth.password.from_value(test_password)

app.container.config.cosmos.db_name.from_value("TestDB")

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    app.container.conversation_database().clear_conversations(test_username)
    yield


@pytest.fixture
def get_token():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    return response.json()["access_token"]


def test_not_authenticated():
    get_response = client.get("/conversation")
    post_response = client.post("/conversation")
    delete_response = client.delete("/conversation")

    assert get_response.status_code == 401
    assert post_response.status_code == 401
    assert delete_response.status_code == 401


def test_get_latest_conversation_creates_new_conversation_when_no_conversation_exists(get_token):
    response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == {"created_at": ANY_STR, "messages": []}


def test_gets_latest_conversation(get_token):
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(
        created_at="2021-01-02T00:00:00", messages=[user_message, bot_message]
    )
    app.container.conversation_database().add_conversation(test_username, conversation_newer)
    app.container.conversation_database().add_conversation(test_username, conversation_older)

    response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(conversation_newer)


def test_creates_new_empty_conversation_when_none_existed(get_token):
    response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == {"created_at": ANY_STR, "messages": []}


def test_creates_new_empty_conversation_when_another_conversation_existed(get_token):
    conversation = Conversation(
        created_at="2021-01-02T00:00:00", messages=[user_message, bot_message]
    )
    app.container.conversation_database().add_conversation(test_username, conversation)

    response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == {"created_at": ANY_STR, "messages": []}


def test_clears_conversations_of_user(get_token):
    response = client.delete("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == "Conversations deleted for user test_user"
