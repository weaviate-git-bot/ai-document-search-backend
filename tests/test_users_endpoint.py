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


def test_not_authenticated():
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_when_authenticated():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    assert access_token
    assert response.json()["token_type"] == "bearer"

    response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"username": test_username}