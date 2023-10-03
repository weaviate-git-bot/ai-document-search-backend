# AI Document Search Backend

[![Lint and test](https://github.com/petr7555/ai-document-search-backend/actions/workflows/lint_and_test.yml/badge.svg)](https://github.com/petr7555/ai-document-search-backend/actions/workflows/lint_and_test.yml)
![Auto-updating coverage badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/petr7555/33a367226c0ebc77e2e059ec7e9204fb/raw/pytest-coverage-comment__master.json)
[![Build and deploy container app to Azure Web App - ai-document-search-backend](https://github.com/petr7555/ai-document-search-backend/actions/workflows/master_ai-document-search-backend.yml/badge.svg)](https://github.com/petr7555/ai-document-search-backend/actions/workflows/master_ai-document-search-backend.yml)
![Supported Python versions](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-blue)

The server is deployed at https://ai-document-search-backend.azurewebsites.net/.
The deployment is automatic on push to the `master` branch.
The OpenAPI schema is available at https://ai-document-search-backend.azurewebsites.net/docs.

This repository uses [Poetry](https://python-poetry.org/) package manager (
see [useful commands](#useful-poetry-commands)).

The server uses [FastAPI](https://fastapi.tiangolo.com/tutorial/) framework.

The code uses [dependency injection](https://python-dependency-injector.ets-labs.org/examples/fastapi.html) and is
tested using [pytest](https://docs.pytest.org/en/stable/).

## How to run the server locally

The server is available at http://localhost:8000/.

Start by creating an `.env` file in the project root with the following content:

```dotenv
APP_OPENAI_API_KEY=your_openai_api_key
APP_WEAVIATE_API_KEY=api_key_for_weaviate_url_specified_in_config
AUTH_SECRET_KEY=any_secret_key
AUTH_USERNAME=any_user
AUTH_PASSWORD=any_password
```

### Without Docker

- `poetry install`
- `poetry run uvicorn ai_document_search_backend.application:app --reload`

### With Docker

- `docker compose up`

## Other useful commands

### Unit tests

- `poetry run pytest`

### Lint autoformat

- `poetry run black --config black.py.toml .`
- `poetry run ruff check . --fix`

### Lint check

- `poetry run black --config black.py.toml . --check`
- `poetry run ruff check .`

### Build Docker image, tag and push to Azure Container Registry

- `docker build -t ai-document-search-backend -f Dockerfile .`
- `docker tag ai-document-search-backend:latest crdocsearchdev.azurecr.io/ai-document-search-backend:0.0.1`
- `docker push crdocsearchdev.azurecr.io/ai-document-search-backend:0.0.1`

### Useful Poetry commands

- Install all dependencies: `poetry install`.
- Add new package at the latest version: `poetry add <package>`, e.g. `poetry add numpy`.
- Add package only for development: `poetry add <package> --group dev`, e.g. `poetry add jupyter --group dev`.
- Regenerate `poetry.lock` file: `poetry lock --no-update`.
- Remove package: `poetry remove <package>`, e.g. `poetry remove numpy`.
