# Data Model Chat Server

A RAG-based agentic chat application built with FastAPI.

## Setup

1.  **Install Dependencies**
    ```bash
    poetry install
    ```

2.  **Configure Environment**
    ```bash
    cp .env.example .env
    ```

## Run

Start the server:
```bash
poetry run python -m src.main
```

The API will be available at `http://localhost:8000`.

## Development

- **Add Dependencies**: `poetry add <package>`
- **Run Tests**: `poetry run pytest`
