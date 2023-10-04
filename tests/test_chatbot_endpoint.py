import pytest
from anys import ANY_STR
from dependency_injector import providers
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app
from ai_document_search_backend.services.auth_service import AuthService

test_username = "test_user"
test_password = "test_password"


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
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
        json={"question": "What is the Loan to value ratio?", "username": test_username},
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
        json={"question": "What is the Loan to value ratio?", "username": test_username},
    )
    assert response.status_code == 200
    assert response.json() == {
        "answer": {
            "text": ANY_STR,
            "sources": [
                {
                    "isin": "NO0010768492",
                    "link": "https://feed.stamdata.com/documents/NO0010768492_LA_20160704.pdf",
                    "page": 8,
                },
                {
                    "isin": "NO0010914682",
                    "link": "https://feed.stamdata.com/documents/NO0010914682_LA_20201217.pdf",
                    "page": 24,
                },
                {
                    "isin": "NO0010914682",
                    "link": "https://feed.stamdata.com/documents/NO0010914682_LA_20201217.pdf",
                    "page": 6,
                },
                {
                    "isin": "NO0010768492",
                    "link": "https://feed.stamdata.com/documents/NO0010768492_LA_20160704.pdf",
                    "page": 4,
                },
            ],
        }
    }
    assert response.json()["answer"]["text"].startswith(
        "The Loan to Value (LTV) ratio is a financial metric"
    )


def test_chat_history(get_token):
    """
    This test runs against real OpenAI API and Weaviate instance.
    APP_OPENAI_API_KEY and APP_WEAVIATE_API_KEY environment variables must be set.
    """
    response = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?", "username": test_username},
    )
    assert response.status_code == 200
    assert response.json()["answer"]["text"].startswith(
        "The Loan to Value (LTV) ratio is a financial"
    )

    response = client.post(
        "/chatbot/",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is it in German?", "username": test_username},
    )
    assert response.status_code == 200
    assert response.json()["answer"]["text"].startswith(
        "Das Loan-to-Value (LTV)-Verhältnis wird auf Deutsch als Beleihungsauslauf bezeichnet."
    )
