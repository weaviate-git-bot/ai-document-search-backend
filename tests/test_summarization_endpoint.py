import pytest

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
    response = client.get("/summarization")
    assert response.status_code == 401


def test_summarize_text(get_token):
    response = client.get(
        "/summarization?text=Hello%20World&summary_length=5",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello"}


def test_missing_text_parameter(get_token):
    response = client.get(
        "/summarization", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["query", "text"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.3/v/missing",
            }
        ]
    }


def test_default_summary_length(get_token):
    response = client.get(
        "/summarization?text=Hello%20World",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello Worl"}
