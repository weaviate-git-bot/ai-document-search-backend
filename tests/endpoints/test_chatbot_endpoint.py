import pytest
from anys import ANY_STR, ANY_LIST, ANY_INT
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

test_username = "test_user"
test_password = "test_password"

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
    assert response.json()["text"] == ANY_STR

    response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 2

    response = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What value should it not exceed?"},
    )
    assert response.status_code == 200
    assert response.json()["text"] == ANY_STR
