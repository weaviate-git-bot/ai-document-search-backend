import pytest
from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

test_username = "test_user"
test_password = "test_password"

app.container.config.auth.secret_key.from_value("test_secret_key")
app.container.config.auth.username.from_value(test_username)
app.container.config.auth.password.from_value(test_password)

client = TestClient(app)


@pytest.fixture
def get_token():
    response = client.post(
        "/auth/token", data={"username": test_username, "password": test_password}
    )
    return response.json()["access_token"]


def test_not_authenticated():
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_when_authenticated(get_token):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json() == {"username": test_username}
