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


client = TestClient(app)


def test_valid_username_and_password():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_invalid_password():
    response = client.post("/auth/token", data={"username": test_username, "password": "invalid"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_invalid_username():
    response = client.post("/auth/token", data={"username": "invalid", "password": test_password})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
