# Project structure, architecture and design

## Package management

This project uses [Poetry](https://python-poetry.org/) for package management.
It can be installed following the official [installation instructions](https://python-poetry.org/docs/#installation).
After it is installed, running `poetry install` in the project root will install all required dependencies according to the [`pyproject.toml`](../pyproject.toml) file.
Poetry creates a virtual environment for the project and installs all dependencies in it. This ensures that the project
dependencies are isolated from the system dependencies.

Here is a list of [useful Poetry commands](../README.md#useful-poetry-commands).

Poetry is used also in the Dockerfile that is used for [local development in Docker](../README.md#with-docker) and for the production deployment.

## Web framework

The server uses [FastAPI](https://fastapi.tiangolo.com/tutorial/) framework.

Endpoints are split by routers which are defined in the [`routers`](../ai_document_search_backend/routers) directory.
The main application is defined in [`application.py`](../ai_document_search_backend/application.py).
Each router defines its prefix (e.g. `/chatbot`). It also defines tags, which group router endpoints in the OpenAPI specification.
The routers are then added to the main application using the `include_router` function.

The endpoints define the request and response models. For non-primitive types, [Pydantic](https://docs.pydantic.dev/latest/) models are used, for example:

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

The code uses [Dependency Injector](https://python-dependency-injector.ets-labs.org/examples/fastapi.html).
This dependency injection framework makes it possible to create a container with all the dependencies and then pass it to the FastAPI application.

The container is defined in [`container.py`](../ai_document_search_backend/container.py).
It loads a configuration from the [`config.yml`](../config.yml) file. The configuration is extended with environment variables.
It then defines factories for services, passing the configuration to them.

The services can then be injected into the routes by using the `@inject` decorator and e.g. `Depends(Provide[Container.chatbot_service])` default parameter.

The unit tests ofter override the container configuration to make the testing easier and independent of the real services.

### Examples

[//]: # (TODO test)

#### Vector database

To use locally running Weaviate DB instead of the instance deployed in [Weaviate Cloud Services](https://console.weaviate.cloud/):

- start Weaviate with `docker compose -f docker-compose-weaviate.yml up -d`
- in [`container.py`](../ai_document_search_backend/container.py), change the `weaviate_client` to use the local Weaviate DB:
    ```python
    weaviate_client = providers.Factory(
        weaviate.Client,
        url="http://localhost:8080",
        additional_headers=providers.Dict(
            {
                "X-OpenAI-Api-Key": config.openai.api_key,
            }
        ),
    )
    ```

#### Database provider

To use an in-memory database instead of Cosmos DB:

- in [`container.py`](../ai_document_search_backend/container.py), change the `conversation_database` to use the in-memory database:
    ```python
    conversation_database = providers.Singleton(
        InMemoryConversationDatabase,
    )
    ```

## Error handling

FastAPI automatically handles unexpected application errors and returns the 500 status code.

A custom `ChatbotError` handler is defined in [`application.py`](../ai_document_search_backend/application.py) to handle exceptions related to answering questions, such as when there are too many tokens sent to OpenAI API.

## Logging

The server uses the standard Python logging library.
The logging configuration is in the [`logging.conf`](../logging.conf) file and is loaded in [`application.py`](../ai_document_search_backend/application.py).
The processing time of all requests is logged using a middleware defined in the same file.

## Authentication

The authentication is done using an OAuth2 password flow with Bearer and JWT tokens. It is heavily inspired by [this FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

The client sends username and password to the `/token` endpoint. The endpoint returns a JWT token which is used to authorize future requests sent to the backend.

The secret key used to encode and decode JWTs is defined in the `AUTH_SECRET_KEY` environment variable.

The database of registered users is hard-coded and consists of a single user with username and password defined in the `AUTH_USERNAME` and `AUTH_PASSWORD` environment variables.

You can find authentication configuration in the `auth` section of the [`config.yml`](../config.yml) file.

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
3. secret keys to be present as environment variables.

See the [key management](#key-management) section for more information about the secret keys.

A code coverage is measured for the unit tests. The ignored files are specified in [`.coveragerc`](../.coveragerc) file.
For more details, see the [CI/CD](#code-coverage) section.

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

See [`Load tests in README.md`](../README.md#load-tests) for instructions on how to run the tests in the UI mode.

## Key management

The secret keys are passed using environment variables.

When running the server or tests locally, the secret keys are loaded from the `.env` file. The `.env` file is not committed to the repository.

When running the tests in GitHub Actions, the secret keys are loaded from the GitHub repository settings. See the `env` section of the GitHub Actions workflow.

The deployed application loads the secret keys from the Azure Web App configuration.

The keys needed for the full server functionality are:

- `APP_OPENAI_API_KEY`
- `APP_WEAVIATE_API_KEY`
- `COSMOS_KEY`
- `AUTH_SECRET_KEY`
- `AUTH_USERNAME`
- `AUTH_PASSWORD`

The keys needed for unit tests are:

- `APP_OPENAI_API_KEY`
- `APP_WEAVIATE_API_KEY`
- `COSMOS_KEY`

- The keys needed for load tests are:
- `AUTH_USERNAME`
- `AUTH_PASSWORD`

## Linting

The backend uses [Ruff](https://github.com/astral-sh/ruff) and [Black](https://github.com/psf/black) for linting and formatting.
The configuration for Ruff is located in the [`pyproject.toml`](../pyproject.toml) file in the `[tool.ruff]` section.
The configuration for Black is located in the [`black.py.toml`](../black.py.toml) file.

## CI/CD

### Linting and unit tests

On every push, GitHub Actions run linting and unit tests (see [`lint_and_test.yml`](../.github/workflows/lint_and_test.yml)).

### Code coverage

Code coverage is collected and added as a commit comment. If the overall code coverage is lower than 70%, the workflow fails.
On push to the `master` branch, the code coverage displayed in the project [`README.md`](../README.md) file is updated.

### Deployment

On every push to the `master` branch, GitHub Actions deploy the backend as an Azure App Service.
See [`master_ai-document-search-backend.yml`](../.github/workflows/master_ai-document-search-backend.yml).
First, a container is built according to the [`Dockerfile`](../Dockerfile) and pushed to the Azure Container Registry.
Then, the container is deployed to the Azure App Service.
There are no pull request preview deployments.
The deployment has been set up using [this tutorial](https://learn.microsoft.com/en-us/azure/app-service/deploy-github-actions?tabs=applevel#use-the-deployment-center).

### Load tests

After the backend is deployed, GitHub Actions run load tests (see [`load_test.yml`](../.github/workflows/load_test.yml)).

## Deployment diagram

![Deployment diagram](diagrams/deployment_diagram.png)

### Server

For server deployment details, see the [CI/CD](#deployment) section.

### Cosmos DB

The server uses [Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/quickstart-python?tabs=azure-portal%2Cconnection-string%2Clinux%2Csign-in-azure-cli%2Csync) as a database to store the conversations.

You can find Cosmos DB configuration in the `cosmos` section of the [`config.yml`](../config.yml) file.
You also need to specify `COSMOS_KEY` environment variable.

### Weaviate

The server uses [Weaviate](https://weaviate.io/) vector database to store the vector representations of the pages of the documents.
It uses a managed instance of Weaviate deployed in [Weaviate Cloud Services](https://console.weaviate.cloud/).

You can find Weaviate configuration in the `weaviate` section of the [`config.yml`](../config.yml) file.
You also need to specify `APP_WEAVIATE_API_KEY` environment variable.

## Chatbot architecture

![Chatbot architecture](diagrams/chatbot_architecture.png)

The chatbot is implemented using [LangChain](https://python.langchain.com/).
LangChain is a framework for developing applications powered by language models.
During the development of this project, LangChain introduced new syntax for creating chains, called [LangChain Expression Language](https://blog.langchain.dev/langchain-expression-language/).
This project is written using the old syntax.

The architecture consists of two main parts – ingestion and RAG chain (Retrieval Augmented Generation).

### Ingestion

The ingestion part is run manually and only once.
For information on how to run the ingestion part, see the [Populating the vector database](../README.md#populating-the-vector-database) section.

The `store` method of the [`ChatbotService`](../ai_document_search_backend/services/chatbot_service.py) loads the PDFs using `PyPDFDirectoryLoader` and converts them to pages of text. It then creates objects which contain the text and also additional metadata such as the page number and ISIN. These objects are then stored in the vector database. Weaviate automatically vectorizes the objects using its `text2vec-openai` module, which uses `text-embedding-ada-002` model from [OpenAI API](https://platform.openai.com/docs/models/embeddings).

Object properties that should be vectorized are defined in the `class_obj` schema (`"skip": False` means that the property is vectorized).

### RAG chain

The RAG chain is run every time the user asks a question.
You can set `verbose: true` in the `chat` section of the [`config.yml`](../config.yml) file to see the prompts that are sent to the models.

The `answer` method of the [`ChatbotService`](../ai_document_search_backend/services/chatbot_service.py) takes the user question, chat history and user-defined filters. Then it calls the `ConversationalRetrievalChain`. This chain first condenses the chat history and the new question using a condense prompt and OpenAI model. Condensing means creating a new standalone question that contains the context of the previous messages.

The number of previous question–answer pairs to take into account when condensing a question is defined by `max_history_length`. The model for condensing is defined by `condense_question_model`. The `get_chat_history` method formats the question–answer pairs. A default condense prompt is used.

The standalone question is then used to retrieve the most relevant objects (pages of text) from the vector database.
The question is vectorized using the `text2vec-openai` module and the most similar objects that match the user filters are returned.
The number of objects to retrieve is defined by `num_sources`.
Weaviate uses [HNSW](https://weaviate.io/developers/weaviate/configuration/indexes#hnsw-vector-indexes) algorithm for vector search.
This is an approximate nearest neighbor (ANN) search algorithm – the results are not guaranteed to be the most similar objects.

The default `StuffDocumentsChain` then creates a `context` by formatting each retrieved object using the `DOCUMENT_PROMPT` prompt and joining them using the default `document_separator= "\n\n"`.
A final prompt is created by pasting the `context` and standalone question into the `QUESTION_PROMPT`. This prompt is sent to the `question_answering_model` which returns the answer.
[//]: # (TODO standalone?)

The answer and the objects previously retrieved from the vector database ("sources") are returned to the user.

### Chatbot configuration

You can find chatbot configuration in the `chatbot` section of the [`config.yml`](../config.yml) file.
For example. changing the `question_answering_model` to `gpt-4` can lead to better answers at the cost of slower response times.
See the comments in the [`config.yml`](../config.yml) file and the [previous section](#rag-chain) for information on what the configuration options mean.

A big influence on the chatbot responses have the prompts.
You can experiment with the `QUESTION_PROMPT` to see how the chatbot responses change.
For example, removing the line "If you can't find an answer, say that you don't know. Don't make things up." results in a chatbot that can tell you a joke.

[//]: # (TODO test joke)

#### Further experimentation

LangChain is a framework that uses chains composed of different components.
These components can be easily replaced with other components.
For example, you can replace the PyPDFLoader with other loaders.

The source documents are combined using the `StuffDocumentsChain` which is further configured using the `DOCUMENT_PROMPT`. You can experiment with [other document chains](https://python.langchain.com/docs/modules/chains/document/).

#### Observability

The scripts folder contains also [`observability.py`](../ai_document_search_backend/scripts/observability.py) file which prints the number of objects in the vector database and the current schema.
The number of objects is equal to the number of pages of all ingested PDFs and can be seen also in the Weaviate Cloud Services dashboard.

## Conversations saving

![Conversations saving](diagrams/conversations_saving.png)
