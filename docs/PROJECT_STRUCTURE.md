# Project structure, architecture and design

## Package management

This project uses [Poetry](https://python-poetry.org/) for package management.
It can be installed following the official [installation instructions](https://python-poetry.org/docs/#installation).
After it is installed, running `poetry install` in the project root will install all required dependencies according to the [`pyproject.toml`](../pyproject.toml) file.
Poetry creates a virtual environment for the project and installs all dependencies in it. This ensures that the project
dependencies are isolated from the system dependencies.

Here is a list of [common Poetry commands](../README.md#useful-poetry-commands).

Poetry is used also in the Dockerfile that is used for local development in Docker and for the production deployment.

## Framework

The server uses [FastAPI](https://fastapi.tiangolo.com/tutorial/) framework.

Endpoints are split by routers which are defined in the [`routers`](../ai_document_search_backend/routers) directory.
The main application is defined in [`application.py`](../ai_document_search_backend/application.py).
Each router defines its prefix. It also defines tags, which group router endpoints in the OpenAPI specification.
The routers are then added to the main application using the `include_router` function.

The endpoints define the request and response models. For non-primitive types, Pydantic models are used, for example:

```python
from pydantic import BaseModel


class ChatbotAnswer(BaseModel):
    text: str
    sources: list[Source]
```

FastAPI automatically validates the request data and returns the 422 status code if the request data is invalid.
It also validates the response data and returns the 500 status code if the response data is invalid.

Based on the request and response models, FastAPI automatically generates the OpenAPI specification which is available at https://ai-document-search-backend.azurewebsites.net/docs.

## Dependency injection

The code uses [dependency injection](https://python-dependency-injector.ets-labs.org/examples/fastapi.html) and is
tested using [pytest](https://docs.pytest.org/en/stable/).

Container

- config file
- e.g. swap cosmos database for in memory database

### local dev

Start Weaviate with `docker compose -f docker-compose-weaviate.yml up -d`.
Change URL in config

### Preprocessing scripts

### Observability scripts

### Mocking

### Authentication

### Error handling

FastAPI automatically handles unexpected application errors and returns the 500 status code.

A custom `ChatbotError` handler is defined in [`application.py`](../ai_document_search_backend/application.py) to handle exceptions related to answering questions, such as when there are too many tokens sent to OpenAI API.

## Testing

### Unit tests

Unit tests are defined in the [`tests`](../tests) directory.
They use the [`pytest`](https://docs.pytest.org/en/stable/) framework.

The [`tests`](../tests) directory structure mirrors the [`ai_document_search_backend`](../ai_document_search_backend) folder structure. The test files are named `test_<name_of_the_tested_file>.py`. The test functions are named `test_<name_of_the_tested_functionality>`.

The test files can contain multiple test functions. The test functions can contain multiple assertions. The assertions can use helpers from the [`anys`](https://github.com/jwodder/anys) library.

Not all files are tested directly. For example, services are tested through routers only.

The router tests use the `TestClient` from the `fastapi.testclient` module to simulate requests to the server.
They also ofter override various container dependencies with mock values.

Keep in mind that some tests use the real dependencies, e.g. a real Cosmos DB, and therefore require:

1. the service to be available,
2. the configration in [`config.yml`](../config.yml) to point to the service,
3. API keys to be present as environment variables.

The environment variables can be set using the `.env` file when running the tests locally. The `.env` file is not committed to the repository.
When running the tests in CI, the variables are set in the GitHub repository settings and pulled into the environment in the `env` section of the GitHub Actions workflow.

#### Coverage

### Load tests

Load testing of the server is done using [Locust](https://locust.io/).

The only focus is on the `/chatbot` endpoint, i.e. answering the user questions.
The tests are defined in [`locustfile.py`](../locustfile.py).
The tests fail if any of the requests returns a non-200 status code or if the average response time of the `/chatbot` endpoint is above 15 seconds.
If the average response time is above 5 seconds, the tests log a warning.
The tests require `AUTH_USERNAME` and `AUTH_PASSWORD` environment variables to be set.

The tests can be run either with the Locust UI or in the headless mode.

The headless mode is used in CI (see [`load_test.yml`](../.github/workflows/load_test.yml)).
It simulates 5 users using the application at the same time for 3 minutes.

See [`README.md`](../README.md#load-tests) for instructions on how to run the tests in UI mode.

## Key management

keys locally
github actions
azure service config

## Linting

Black
Ruff
Files with rules, project.toml

## CI/CD

On every push, GitHub Actions run linting and unit tests (see [`lint_and_test.yml`](../.github/workflows/lint_and_test.yml)).
Code coverage is collected and added as a commit comment. If the overall code coverage is lower than 70%, the workflow fails.
On push to the `master` branch, the code coverage displayed in the project README.md file is updated.
(see [`pytest-coverage-comment.yml`](../.github/workflows/pytest-coverage-comment.yml)).

On every push to the `master` branch, GitHub Actions deploy the backend as an Azure Web App.
See [`master_ai-document-search-backend.yml`](../.github/workflows/master_ai-document-search-backend.yml).
There are no pull request preview deployments.
After the backend is deployed, GitHub Actions run load tests (see [`load_test.yml`](../.github/workflows/load_test.yml)).

Lint
Load
Coverage comments
No preview deployment

### Deployment diagram

## Chatbot architecture

## Conversations saving 
