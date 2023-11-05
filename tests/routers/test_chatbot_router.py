import pytest
from anys import ANY_STR, ANY_LIST, ANY_INT, ANY_FLOAT
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


def test_not_authenticated_root_endpoint():
    response = client.post(
        "/chatbot/",
        json={"question": "What is the Loan to value ratio?", "filters": []},
    )
    assert response.status_code == 401


def test_not_authenticated_filter_endpoint():
    response = client.get("/chatbot/filter")
    assert response.status_code == 401


def test_chatbot_response(get_token):
    """
    This test runs against real OpenAI API and Weaviate instance.
    APP_OPENAI_API_KEY and APP_WEAVIATE_API_KEY environment variables must be set.
    """
    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?", "filters": []},
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
        "certainty": ANY_FLOAT,
        "distance": ANY_FLOAT,
    }


def test_chat_history(get_token):
    """
    This test runs against real OpenAI API and Weaviate instance.
    APP_OPENAI_API_KEY and APP_WEAVIATE_API_KEY environment variables must be set.
    """
    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?", "filters": []},
    )
    assert response.status_code == 200
    assert response.json()["text"] == ANY_STR

    response = client.get("/conversation", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 2

    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What value should it not exceed?", "filters": []},
    )
    assert response.status_code == 200
    assert response.json()["text"] == ANY_STR


def test_gets_available_filters(get_token):
    response = client.get("/chatbot/filter", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {
        "isin": ANY_LIST,
        "issuer_name": ANY_LIST,
        "filename": ANY_LIST,
        "industry": ANY_LIST,
        "risk_type": ANY_LIST,
        "green": ANY_LIST,
    }
    assert response_data["isin"][0] == ANY_STR
    assert response_data["issuer_name"][0] == ANY_STR
    assert response_data["filename"][0] == ANY_STR
    assert response_data["industry"][0] == ANY_STR
    assert response_data["risk_type"][0] == ANY_STR
    assert response_data["green"][0] == ANY_STR


@pytest.mark.parametrize(
    "filters",
    [
        [],
        [{"property_name": "isin", "values": []}],
        [
            {"property_name": "isin", "values": []},
            {"property_name": "industry", "values": ["Real Estate - Commercial"]},
        ],
        [{"property_name": "isin", "values": ["NO1111111111"]}],
        [{"property_name": "isin", "values": ["NO1111111111", "NO2222222222"]}],
        [
            {"property_name": "isin", "values": ["NO1111111111"]},
            {"property_name": "industry", "values": ["Real Estate - Commercial"]},
        ],
        [
            {"property_name": "isin", "values": ["NO1111111111", "NO2222222222"]},
            {
                "property_name": "industry",
                "values": ["Real Estate - Commercial", "Real Estate - Residential"],
            },
        ],
    ],
)
def test_filters(get_token, filters):
    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"question": "What is the Loan to value ratio?", "filters": filters},
    )
    assert response.status_code == 200


def test_invalid_filter_property_name():
    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={
            "question": "What is the Loan to value ratio?",
            "filters": [{"property_name": "invalid", "values": []}],
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "expected": "'isin', 'issuer_name', 'filename', "
                    "'industry', 'risk_type' or 'green'"
                },
                "input": "invalid",
                "loc": ["body", "filters", 0, "property_name"],
                "msg": "Input should be 'isin', 'issuer_name', 'filename', "
                "'industry', 'risk_type' or 'green'",
                "type": "literal_error",
                "url": "https://errors.pydantic.dev/2.3/v/literal_error",
            }
        ]
    }


def test_chatbot_exception_when_message_is_too_long(get_token):
    response = client.post(
        "/chatbot",
        headers={"Authorization": f"Bearer {get_token}"},
        json={
            "question": "Text" * 5000,
            "filters": [],
        },
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data == {
        "detail": ANY_STR,
    }
    assert response_data["detail"].startswith(
        "Error while answering question: This model's maximum context length is"
    )
