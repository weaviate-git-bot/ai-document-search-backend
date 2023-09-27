from fastapi.testclient import TestClient
from datetime import timedelta
from jose import jwt


from ai_document_search_backend.application import app
from ai_document_search_backend.auth import create_access_token
from ai_document_search_backend.auth import get_hashed_password, check_password
from ai_document_search_backend.config import Settings


client = TestClient(app)


def test_valid_authentication():
    response = client.post("/auth/token", data={"username": "marius", "password": 123})
    assert response.status_code == 200


def test_invalid_password():
    response = client.post("/auth/token", data={"username": "marius", "password": 1231})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}


def test_invalid_username():
    response = client.post("/auth/token", data={"username": "maris", "password": 123})
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}


def test_hashing():
    password = "password"
    hashed_password = get_hashed_password(password)
    assert check_password(password, hashed_password)


def test_token():
    secretkey = Settings().secretkey
    algorithm = "HS256"
    access_token_expire_minutes = 60

    username = "testuser"

    token_expires = timedelta(minutes=access_token_expire_minutes)
    token = create_access_token(data={"sub": username}, expires_delta=token_expires)

    response = client.get("/auth/validate_token", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200

    payload = jwt.decode(token, secretkey, algorithms=[algorithm])
    username: str = payload.get("sub")

    assert username == "testuser"
