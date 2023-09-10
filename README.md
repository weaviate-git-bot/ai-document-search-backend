# AI Document Search Backend

![Auto-updating coverage badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/petr7555/33a367226c0ebc77e2e059ec7e9204fb/raw/pytest-coverage-comment__master.json)

## How to run

### Server

#### Without Docker

- `poetry run uvicorn ai_document_search_backend.application:app --reload`

#### With Docker

- `docker compose up`

### Unit tests

- `poetry run pytest`

### Lint autoformat

- `poetry run black --config black.py.toml .`

### Lint check

- `poetry run black --config black.py.toml . --check`
