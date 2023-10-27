from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

test_username = "test_user"
test_password = "test_password"

app.container.config.auth.secret_key.from_value("test_secret_key")
app.container.config.auth.username.from_value(test_username)
app.container.config.auth.password.from_value(test_password)

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
