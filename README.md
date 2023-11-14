# AI Document Search Backend

[![Lint and test](https://github.com/petr7555/ai-document-search-backend/actions/workflows/lint_and_test.yml/badge.svg)](https://github.com/petr7555/ai-document-search-backend/actions/workflows/lint_and_test.yml)
[![Load test](https://github.com/petr7555/ai-document-search-backend/actions/workflows/load_test.yml/badge.svg)](https://github.com/petr7555/ai-document-search-backend/actions/workflows/load_test.yml)
![Auto-updating coverage badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/petr7555/33a367226c0ebc77e2e059ec7e9204fb/raw/pytest-coverage-comment__master.json)
[![Build and deploy container app to Azure Web App - ai-document-search-backend](https://github.com/petr7555/ai-document-search-backend/actions/workflows/master_ai-document-search-backend.yml/badge.svg)](https://github.com/petr7555/ai-document-search-backend/actions/workflows/master_ai-document-search-backend.yml)
![Supported Python versions](https://img.shields.io/badge/Python-3.9-blue)

The server is deployed at https://ai-document-search-backend.azurewebsites.net/.
The deployment is automatic on push to the `master` branch.
The OpenAPI schema is available at https://ai-document-search-backend.azurewebsites.net/docs.

This repository uses [Poetry](https://python-poetry.org/) package manager (see [useful commands](#useful-poetry-commands)).

The server uses [FastAPI](https://fastapi.tiangolo.com/tutorial/) framework.

The code uses [dependency injection](https://python-dependency-injector.ets-labs.org/examples/fastapi.html) and is
tested using [pytest](https://docs.pytest.org/en/stable/).

## How to run the server locally

The server is available at http://localhost:8000.

Start by creating an `.env` file in the project root with the following content:

```dotenv
APP_OPENAI_API_KEY=your_openai_api_key
APP_WEAVIATE_API_KEY=api_key_for_weaviate_url_specified_in_config
COSMOS_KEY=key_for_cosmos_url_specified_in_config
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

### Load tests

- Start the server locally (see above).
- `poetry run locust`
- Open http://localhost:8089/ in your browser.
- Enter the number of users, the spawn rate and Host (http://localhost:8000 – without trailing slash).
- Click "Start swarming".

### Lint autoformat

- `poetry run black --config black.py.toml .`
- `poetry run ruff check . --fix`

### Lint check

- `poetry run black --config black.py.toml . --check`
- `poetry run ruff check .`

### Build Docker image, tag and push to Azure Container Registry

- `docker build -t ai-document-search-backend -f Dockerfile .`
- `docker tag ai-document-search-backend:latest crdocsearchdev.azurecr.io/crdocsearchdev/ai-document-search-backend:0.0.1`
- `az login`
- `az acr login --name crdocsearchdev`
- `docker push crdocsearchdev.azurecr.io/crdocsearchdev/ai-document-search-backend:0.0.1`

### Useful Poetry commands

- Install all dependencies: `poetry install`.
- Add new package at the latest version: `poetry add <package>`, e.g. `poetry add numpy`.
- Add package only for development: `poetry add <package> --group dev`, e.g. `poetry add jupyter --group dev`.
- Regenerate `poetry.lock` file: `poetry lock --no-update`.
- Remove package: `poetry remove <package>`, e.g. `poetry remove numpy`.

### Populating the vector database

- Download `NTNU2.xlsx` from the customer and save it to `data/NTNU2.xlsx`. This file is private and is therefore not included in the repository.
  See [`prepare_data.py`](ai_document_search_backend/scripts/prepare_data.py) for the columns that must be present in the file.
- Run `poetry run python ai_document_search_backend/scripts/prepare_data.py` to pre-process the data.
- Run `poetry run python ai_document_search_backend/scripts/download_documents.py [limit]` to download the PDFs into a local folder. The limit is optional and specifies the number of documents to download. If not specified, all documents will be downloaded.
- Run `poetry run python ai_document_search_backend/scripts/fill_vectorstore.py` to store the documents in the vector database.

## Project structure, architecture and design

For a more detailed description of the project structure, architecture and design, see the [project structure](docs/PROJECT_STRUCTURE.md) document.
