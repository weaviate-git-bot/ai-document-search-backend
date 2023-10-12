import pytest
from anys import ANY_STR, ANY_LIST, ANY_INT
from dependency_injector import providers
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app
from ai_document_search_backend.services.auth_service import AuthService

test_username = "test_user"
test_password = "test_password"


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # reset the conversation history before each test
    app.container.conversation_database.reset()

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
    yield
    app.container.auth_service.reset_override()


@pytest.fixture
def get_token():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    return response.json()["access_token"]


client = TestClient(app)


def test_not_authenticated():
    response = client.post(
        "/chatbot/",
        json={"question": "What is the Loan to value ratio?"},
    )
    assert response.status_code == 401


def test_chatbot_response(get_token):
    """
    This test runs against real OpenAI API and Weaviate instance.
    APP_OPENAI_API_KEY and APP_WEAVIATE_API_KEY environment variables must be set.
    """
    response = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {
        "text": ANY_STR,
        "sources": ANY_LIST,
    }
    assert "The Loan to Value (LTV) ratio" in response_data["text"]
    assert response_data["sources"][0] == {
        "isin": ANY_STR,
        "shortname": ANY_STR,
        "link": ANY_STR,
        "page": ANY_INT,
    }


def test_chat_history(get_token):
    """
    This test runs against real OpenAI API and Weaviate instance.
    APP_OPENAI_API_KEY and APP_WEAVIATE_API_KEY environment variables must be set.
    """
    response = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?"},
    )
    assert response.status_code == 200
    assert "The Loan to Value" in response.json()["text"]

    response2 = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What value should it not exceed?"},
    )
    assert response2.status_code == 200
    assert "The Loan to Value ratio should not exceed" in response2.json()["text"]
