# FastAPI Server Template - Architecture

## Overview

A production-ready FastAPI server template with a focus on vertical slice architecture, scalability, and developer experience. It provides a solid foundation for building new web applications and APIs.

**Core Principles**: Async-first, type-safe, modular design with clean separation of concerns.

---

## Technology Stack

### Core Framework
- **FastAPI** - Modern async web framework with automatic OpenAPI documentation.
- **Uvicorn[standard]** - ASGI server with WebSocket and high-performance capabilities.
- **Python** (≥3.12) - Modern Python with a rich type system.

### Database & ORM
- **SQLAlchemy** (2.0+) - Modern ORM with full async support.
- **AsyncPG** - High-performance asynchronous PostgreSQL driver.
- **Psycopg2** - PostgreSQL adapter for Alembic migrations.
- **Alembic** - Database migration management tool.
- **PostgreSQL** - Recommended relational database (external).

### Security & Authentication
- **PyJWT[crypto]** - JWT token generation and validation.
- **Passlib[bcrypt]** - Password hashing library with bcrypt support.
- **Bcrypt** - Secure password hashing algorithm.

### Configuration & Validation
- **Pydantic[email]** - Data validation with email support.
- **Pydantic-settings** - Environment-based configuration management.

### API Features
- **SlowAPI** - Rate limiting middleware.
- **HTTPX** - Async HTTP client for external API calls.
- **WebSockets** - Built-in support for real-time communication.
- **NH3** - HTML sanitization for user-generated content.

### Dependency Management
- **Poetry** - Modern dependency and package manager.

### Development Tools
- **Pre-commit** - Git hook framework for code quality.
- **Black** - Opinionated code formatter.
- **Ruff** - Fast Python linter.
- **MyPy** - Static type checker.

---

## Project Structure

### Root Directory
```
fastapi-server-template/
├── .env                     # Environment variables (gitignored)
├── .env.example             # Environment variable template
├── .gitignore              # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Poetry dependencies & project metadata
├── poetry.lock             # Locked dependency versions
├── README.md               # Project documentation
├── docs/                   # Documentation files
│   └── ARCHITECTURE.md     # This file
├── migrations/             # Alembic database migrations
│   ├── env.py             # Alembic environment configuration
│   ├── script.py.mako     # Migration template
│   └── versions/          # Migration version files
└── src/                    # Source code
```

### Source Code Structure
```
src/
├── __init__.py             # Package marker
├── main.py                 # Application entry point
│
├── api/                    # API router aggregation
│   ├── __init__.py
│   └── router.py          # Main API router combining all modules
│
├── auth/                   # Authentication & user management
│   ├── __init__.py
│   ├── models.py          # User SQLAlchemy model
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── security.py        # JWT & password hashing utilities
│   ├── service.py         # Business logic (registration, login)
│   ├── dependencies.py    # FastAPI auth dependencies
│   ├── router.py          # Auth API endpoints
│   └── exceptions.py      # Auth-specific exceptions
│
├── core/                   # Shared infrastructure
│   ├── __init__.py
│   ├── config.py          # Pydantic Settings configuration
│   ├── exceptions.py      # Base exception & global handlers
│   ├── middleware.py      # CORS, rate limiting, etc.
│   ├── logging.py         # Logging configuration
│   └── health.py          # Health check endpoints
│
├── db/                     # Database layer
│   ├── __init__.py
│   ├── database.py        # Async engine, session factory
│   └── models.py          # Base model definition
│
├── realtime/               # Generic WebSocket pub/sub system
│   ├── __init__.py
│   ├── connection_manager.py # Manages WebSocket connections
│   ├── router.py             # WebSocket pub/sub endpoints
│   ├── notify.py             # Server-side notification utilities
│   └── schemas.py            # Pydantic schemas for WebSocket communication
│
└── utils/                  # Miscellaneous utilities
    ├── __init__.py
    ├── sanitizer.py         # HTML sanitization utility
    └── image_utils.py       # Image and file handling utility
```

---

## Architecture Patterns

### Request Flow
```
Client Request
    ↓
Uvicorn ASGI Server
    ↓
ProcessTimeMiddleware (request timing)
    ↓
CORSMiddleware (cross-origin handling)
    ↓
SlowAPI Rate Limiter
    ↓
FastAPI Router
    ↓
Authentication Dependency (if required)
    ↓
Route Handler
    ↓
Service Layer (business logic)
    ↓
Database Session (SQLAlchemy async)
    ↓
Response (JSON / WebSocket)
```

### Middleware Order
1. **ProcessTimeMiddleware** - Logs request duration and adds `X-Process-Time` header.
2. **CORSMiddleware** - Handles cross-origin resource sharing.
3. **Rate Limiter** - Enforces request rate limits.
4. **FastAPI Routing** - Matches routes and handles dependency injection.

### Async Architecture
- Fully asynchronous stack from web server to database.
- **AsyncPG** provides non-blocking PostgreSQL operations.
- Async session management with automatic commit/rollback via `Depends(get_db)`.
- Concurrent request handling without threading overhead.

### Dependency Injection
FastAPI's DI system provides:
- **Database sessions** per request (`Depends(get_db)`).
- **Authentication** via custom dependencies (e.g., `ValidToken`).
- **Type-annotated dependencies** for clarity and type safety.

---

## Authentication System

### JWT-Based Stateless Authentication

**Token Structure**:
- `user_id` (int): Unique user identifier.
- `token_type` (str): "access".
- `exp` (datetime): Token expiration.

**Configuration**:
- **Algorithm**: HS256 (configurable via `JWT_ALGORITHM`).
- **Secret Key**: Set via `JWT_SECRET_KEY` (**must be changed in production**).
- **Expiration**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`.

**Password Security**:
- **Hashing**: Bcrypt with automatic salting via Passlib.
- No plaintext passwords are ever stored or logged.

### API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/auth/register` | POST | No | Create a new user account. |
| `/api/auth/login` | POST | No | Authenticate and get a JWT token. |
| `/api/auth/me` | GET | Yes | Get the current authenticated user's profile. |
| `/api/auth/users` | GET | Yes | List all users in the system. |

---

## Real-time Notification System

A generic WebSocket-based system for real-time, topic-based publish/subscribe communication.

### Connection Management (`ConnectionManager`)
- Manages active WebSocket connections.
- Allows clients to subscribe to arbitrary string-based "topics".
- Provides a method to broadcast messages to all clients subscribed to a specific topic.

### Endpoint and Behavior
| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/ws/{topic}` | WebSocket | Yes | Establishes a WebSocket connection and subscribes the client to the specified topic. |

- **Authentication**: The `WSValidToken` dependency ensures that only authenticated users can establish a WebSocket connection.
- **Pub/Sub Relay**: Once connected, a client can send any JSON message as long as it contains both a `topic` and a `type` key (e.g., `{"topic": "general", "type": "event_name", ...}`). The server validates that the `topic` in the message body matches the topic in the URL, then broadcasts the original JSON object to all other clients on that topic.

---

## Database Layer

### Connection Configuration
- **Async Engine**: `create_async_engine` with connection pooling.
- **URL**: Configured via environment variables, using `asyncpg` driver.
- **Sync URL**: A separate sync URL is provided for Alembic migrations (`psycopg2` driver).

### Session Management
- **Per-request sessions** provided by the `get_db` dependency.
- **Automatic transaction management**: Commits on success, rolls back on error.

### Data Models
- **Base Class**: All models inherit from a `DeclarativeBase`.
- **Current Models**: `User` model for the authentication system.
- **Typed Mappings**: Uses `Mapped[T]` for type safety.

### Migrations (Alembic)
- **Configuration**: Managed in `alembic.ini` and `migrations/env.py`.
- **URL**: Dynamically set from application settings.
- **Commands**: Standard `alembic revision`, `upgrade`, `downgrade` commands.

---

## Exception Handling

### Hierarchy
A custom `AppError` serves as the base for all domain-specific exceptions, like those in the `auth` module.

### Global Handlers
Registered in `src/core/exceptions.py`:
- **AppError Handler**: Catches custom exceptions and returns structured JSON.
- **HTTPException Handler**: Catches FastAPI/Starlette HTTP exceptions.
- **RequestValidationError Handler**: Handles Pydantic validation errors (422).
- **RateLimitExceeded Handler**: Manages rate limit violations (429).
- **Generic Handler**: A catch-all for any unhandled exceptions (500).

All handlers log the error and return a consistent JSON response.

---

## Configuration Management

### Pydantic Settings
- **Source**: `src/core/config.py` using `pydantic-settings`.
- **Priority**: 1. Environment variables, 2. `.env` file, 3. Default values.

### Key Configuration Categories
- **Server**: `HOST`, `PORT`, `ENVIRONMENT`.
- **Rate Limiting**: `RATE_LIMIT`.
- **Database**: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (default: "templatedb").
- **JWT**: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- **CORS**: `CORS_ORIGINS`.
- **File Storage**: `BASE_IMAGE_PATH`.
---

## Logging System

### Configuration (`src/core/logging.py`)
- **Directory**: The `logs/` directory is used for file-based logging. Note: This directory is gitignored and must be created if it doesn't exist.
- **Format**: `[timestamp] [logger_name] [level] message`.
- **Handlers**: `StreamHandler` (console) and `FileHandler` (`logs/`).

### Logged Events
- **INFO**: Successful requests with duration.
- **WARNING**: Handled errors like validation failures or invalid tokens.
- **ERROR**: Unhandled exceptions with stack traces.

---

## Code Quality (Pre-commit)

Pre-commit hooks are configured in `.pre-commit-config.yaml` to run automatically on `git commit`.
- **`black`**: For code formatting.
- **`ruff`**: For linting and auto-fixing.
- **`mypy`**: For static type checking.

---

## Development Workflow

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd fastapi-server-template

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and a new JWT_SECRET_KEY

# Set up pre-commit hooks
poetry run pre-commit install

# Run database migrations
poetry run alembic upgrade head
```

### Development Server
```bash
poetry run python -m src.main
```
The server runs with auto-reload in development.

---

## Summary

This **FastAPI Server Template** provides:

### ✅ Core Features
- **Authentication System**: JWT-based auth with registration, login, and user management.
- **Database Layer**: Async SQLAlchemy with connection pooling and Alembic migrations.
- **API Framework**: FastAPI with automatic OpenAPI documentation.
- **Real-time Notifications**: Generic topic-based WebSocket system.
- **Configuration**: Environment-based settings with Pydantic validation.
- **Logging**: Structured logging with file and console output.
- **Middleware**: CORS, rate limiting, and request timing.
- **Exception Handling**: Centralized error handling.
- **Code Quality**: Pre-commit hooks with formatting, linting, and type checking.
- **Health Checks**: Database connectivity and uptime monitoring.

### 📚 Documentation
- **ARCHITECTURE.md**: This file, detailing the system architecture.
