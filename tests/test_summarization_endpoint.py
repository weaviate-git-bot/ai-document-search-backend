from fastapi.testclient import TestClient

from ai_document_search_backend.application import app

client = TestClient(app)


def test_summarize_text():
    response = client.get("/summarization?text=Hello%20World&summary_length=5")
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello"}


def test_missing_text_parameter():
    response = client.get("/summarization")
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


def test_default_summary_length():
    response = client.get("/summarization?text=Hello%20World")
    assert response.status_code == 200
    assert response.json() == {"summary": "Hello Worl"}
