from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "OK"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "OK"
