import os
from dotenv import load_dotenv
import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app
from ai_document_search_backend.database_providers.cosmos_database import CosmosDBConversationDatabase
from ai_document_search_backend.services.auth_service import AuthService

test_username = "test_user"
test_password = "test_password"

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # reset the conversation history before each test
    app.container.conversation_database.reset()

    load_dotenv()

    app.container.auth_service.override(
        providers.Factory(
            AuthService,
            algorithm="HS256",
            access_token_expire_minutes=30,
            secret_key="test_secret_key",
            username=test_username,
            password=test_password,
        )
    )
    app.container.conversation_database.override(providers.Singleton(
        # InMemoryConversationDatabase,
        CosmosDBConversationDatabase,
        endpoint = os.getenv("COSMOS_ENDPOINT"),
        key = os.getenv("COSMOS_KEY"),
        db_name = "Test"
    ))
    yield
    app.container.auth_service.reset_override()
    app.container.conversation_database.reset_override()


@pytest.fixture
def get_token():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    return response.json()["access_token"]


client = TestClient(app)

def test_not_authenticated():
    get_response = client.get("/conversation/")
    post_response = client.post("/conversation")

    assert get_response.status_code == 401
    assert post_response.status_code == 401

def test_create_conversation(get_token):
    post_response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    print(f"Bearer {get_token}")
    assert post_response.status_code == 200

def test_add_to_conversation(get_token):
    post_response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert post_response.status_code == 200

    chat_response = client.post("/chatbot", headers={"Authorization": f"Bearer {get_token}"}, json={"question": "What is the Loan to value ratio?"})
    assert chat_response.status_code == 200

    get_response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert get_response.status_code == 200
    assert len(get_response.json()['messages']) == 2


def test_create_new_conversation(get_token):
    post_response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert post_response.status_code == 200

    chat_response = client.post("/chatbot", headers={"Authorization": f"Bearer {get_token}"}, json={"question": "What is the Loan to value ratio?"})
    assert chat_response.status_code == 200

    get_response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert get_response.status_code == 200
    assert len(get_response.json()['messages']) == 2

    post_response = client.post("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert post_response.status_code == 200

    get_response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert get_response.status_code == 200
    assert len(get_response.json()['messages']) == 0