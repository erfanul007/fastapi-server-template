# Data Model Chat Server

A RAG-based agentic chat application built with FastAPI.

**Requirements**: Python 3.12
**Status**: ✅ Auth & Infrastructure | 🔄 Chat, RAG, Agents (Planned)

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
poetry run pytest                      # Run tests (when available)
```

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Current system architecture
- [ROADMAP.md](docs/ROADMAP.md) - Development roadmap
