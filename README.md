# FastAPI Server Template

A production-ready FastAPI server template with a focus on vertical slice architecture, scalability, and developer experience.

**Requirements**: Python 3.12

## Features

-   **FastAPI**: High-performance web framework.
-   **SQLAlchemy 2.0**: Asynchronous database operations.
-   **Pydantic**: Robust data validation and settings management.
-   **Alembic**: Database migrations.
-   **JWT Authentication**: Secure user authentication.
-   **Dependency Injection**: Decoupled and testable components.
-   **Vertical Slice Architecture**: Organized by feature for better maintainability.
-   **Structured Logging**: Centralized and configurable logging.
-   **Global Exception Handling**: Consistent error responses.
-   **CORS & Rate Limiting**: Essential security middleware.
-   **Health Checks**: Monitor application status.
-   **WebSocket Support**: Generic real-time notification system.
-   **Pre-commit Hooks**: Automated code quality checks with `black`, `ruff`, and `mypy`.

## Setup

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Set up pre-commit hooks
poetry run pre-commit install

# Run database migrations
poetry run alembic upgrade head
```

## Run

```bash
poetry run python -m src.main
```

API available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

**Add Dependencies**
```bash
poetry add <package>              # Production dependency
poetry add --group dev <package>  # Dev dependency
```

**Database Migrations**
```bash
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
```

**Code Quality**
```bash
poetry run pre-commit run --all-files  # Run all checks
```

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
