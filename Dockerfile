ARG PYTHON_VERSION=3.9
FROM python:$PYTHON_VERSION

LABEL name="python-$PYTHON_VERSION"
LABEL version="$PYTHON_VERSION"
LABEL maintainer="Petr Janik <petrj@stud.ntnu.no>"

ARG POETRY_VERSION=1.3.2

# Install Poetry system-wide using pip
RUN pip install --upgrade pip && \
    pip install poetry==${POETRY_VERSION}

WORKDIR /ai_document_search_backend

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --only main --no-root --no-cache --no-interaction

COPY ai_document_search_backend ./ai_document_search_backend

CMD ["poetry", "run", "uvicorn", "ai_document_search_backend.application:app", "--host", "0.0.0.0", "--port", "8080"]
