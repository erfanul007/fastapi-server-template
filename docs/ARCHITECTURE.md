# Data Model Chat Server - Architecture

## Overview

A RAG-based agentic chat application built with FastAPI. Currently implements a production-ready authentication system with database management.

**Core Principles**: Async-first, type-safe, modular design with clean separation of concerns.

---

## Technology Stack

### Core Framework
- **FastAPI** (≥0.123.9, <0.124.0) - Modern async web framework with automatic OpenAPI documentation
- **Uvicorn[standard]** (≥0.38.0, <0.39.0) - ASGI server with standard extensions (websockets, httptools, uvloop)
- **Python** (≥3.12, <3.13) - Required Python version with modern type system

### Database & ORM
- **SQLAlchemy** (≥2.0.44, <3.0.0) - Modern ORM with full async support and typed `Mapped` annotations
- **AsyncPG** (≥ 0.31.0, <0.32.0) - High-performance PostgreSQL async driver
- **Psycopg2** (≥2.9.11, <3.0.0) - PostgreSQL adapter used by Alembic for migrations
- **Alembic** (≥1.17.2, <2.0.0) - Database migration management tool
- **PostgreSQL** - Relational database (external dependency)

### Security & Authentication
- **PyJWT[crypto]** (≥2.10.1, <3.0.0) - JWT token generation/validation with cryptographic signing
- **Passlib[bcrypt]** (≥1.7.4, <2.0.0) - Password hashing library with bcrypt support
- **Bcrypt** (==4.3.0) - Secure password hashing algorithm

### Configuration & Validation
- **Pydantic[email]** (≥2.12.5, <3.0.0) - Data validation with email validation support
- **Pydantic-settings** (≥2.12.0, <3.0.0) - Environment-based configuration management

### API Features
- **SlowAPI** (≥0.1.9, <0.2.0) - Rate limiting middleware for FastAPI
- **HTTPX** (≥0.28.1, <0.29.0) - Async HTTP client for external API calls

### Dependency Management
- **Poetry** (2.0+) - Modern dependency and package manager
  - Uses **PEP 621** (`pyproject.toml` [project] table) for metadata
  - **Poetry Core** (≥2.0.0, <3.0.0) as build backend
  - Package mode disabled (`package-mode = false`)
  - Dependency groups for separating dev dependencies

### Development Tools
- **Pre-commit** (≥4.5.0, <5.0.0) - Git hook framework
- **Black** (≥25.11.0, <26.0.0) - Opinionated code formatter
- **Ruff** (≥0.14.8, <0.15.0) - Fast Python linter
- **MyPy** (≥1.19.0, <2.0.0) - Static type checker

---

## Project Structure

### Root Directory
```
data-model-chat-server/
├── .env                     # Environment variables (gitignored)
├── .env.example             # Environment variable template
├── .gitignore              # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Poetry dependencies & project metadata
├── poetry.lock             # Locked dependency versions
├── README.md               # Project documentation
├── docs/                   # Documentation files
│   ├── ARCHITECTURE.md     # This file
│   └── ROADMAP.md          # Development roadmap
├── logs/                   # Application logs (timestamped files)
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
│   ├── dependencies.py    # FastAPI auth dependencies (token validation)
│   ├── router.py          # Auth API endpoints
│   └── exceptions.py      # Auth-specific exceptions
│
├── core/                   # Shared infrastructure
│   ├── __init__.py
│   ├── config.py          # Pydantic Settings configuration
│   ├── exceptions.py      # Base exception & global handlers
│   ├── middleware.py      # CORS, rate limiting, process time tracking
│   ├── logging.py         # Logging configuration
│   └── health.py          # Health check endpoints
│
└── db/                     # Database layer
    ├── __init__.py
    └── database.py        # Async engine, session factory, dependency
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
SlowAPI Rate Limiter (rate limit enforcement)
    ↓
FastAPI Router (route matching)
    ↓
Authentication Dependency (if required)
    ↓
Route Handler (controller)
    ↓
Service Layer (business logic)
    ↓
Database Session (SQLAlchemy async)
    ↓
Response (JSON)
```

### Middleware Order
1. **ProcessTimeMiddleware** - Custom middleware that logs request duration and adds `X-Process-Time` header
2. **CORSMiddleware** - Starlette middleware for cross-origin resource sharing
3. **Rate Limiter** - SlowAPI state attached to app, enforced via decorators/dependencies
4. **FastAPI Routing** - Route matching and dependency injection

### Async Architecture
- **Full async/await stack** from web server to database
- **AsyncPG** provides non-blocking PostgreSQL operations
- **Async session management** with automatic commit/rollback in `get_db()` dependency
- **Concurrent request handling** without threading overhead
- **Connection pooling** managed by SQLAlchemy async engine

### Dependency Injection
FastAPI's dependency injection system provides:
- **Database sessions** injected per request via `Depends(get_db)`
- **Authentication** via `Depends(oauth2_scheme)` and custom dependencies
- **Type-annotated dependencies** for IDE autocomplete and type checking
- **Nested dependencies** (e.g., `get_current_user` depends on `oauth2_scheme`)

---

## Authentication System

### JWT-Based Stateless Authentication

**Token Structure** (TokenData schema):
- `user_id` (int) - Unique user identifier
- `token_type` (str) - Always "access" for access tokens
- `exp` (datetime) - Token expiration timestamp

**Configuration**:
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Configurable via `JWT_SECRET_KEY` environment variable
- **Expiration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

**Password Security**:
- **Hashing**: Bcrypt with automatic salting
- **Passlib CryptContext** with bcrypt as the active scheme
- **No plaintext passwords** stored or logged

### Authentication Flow

1. **Registration** (`POST /api/auth/register`):
   - Validate email uniqueness
   - Hash password with bcrypt
   - Create user in database
   - Return user data (no token)

2. **Login** (`POST /api/auth/login`):
   - Verify email exists
   - Verify password hash
   - Generate JWT token
   - Return access token

3. **Protected Endpoints**:
   - Extract bearer token from `Authorization` header
   - Decode and validate JWT
   - Verify token type and expiration
   - Load user from database
   - Inject authenticated user into route handler

### API Endpoints

| Endpoint | Method | Auth | Description | Response |
|----------|--------|------|-------------|----------|
| `/api/auth/register` | POST | No | Create new user account | UserRead (201) |
| `/api/auth/login` | POST | No | Authenticate and get token | LoginResponse (200) |
| `/api/auth/me` | GET | Yes | Get current user profile | UserRead (200) |
| `/api/auth/users` | GET | Yes | List all users | List[UserRead] (200) |

### OAuth2 Integration
Uses FastAPI's `OAuth2PasswordBearer` scheme with `tokenUrl="auth/login"` for OpenAPI documentation.

---

## Database Layer

### Connection Configuration

**Async Engine** (`create_async_engine`):
- **URL Format**: `postgresql+asyncpg://user:password@host:port/dbname`
- **Echo**: Enabled in development for SQL logging
- **Pool Pre-ping**: Enabled to verify connection health before use
- **Connection Pooling**: Managed by SQLAlchemy (default pool size)

**Session Factory** (`async_sessionmaker`):
- **expire_on_commit=False**: Prevents lazy loading issues after commit
- **autoflush=False**: Manual control over flush operations

**Dual URLs**:
- **Async URL** (`database_url`): Used by application runtime (asyncpg driver)
- **Sync URL** (`database_url_sync`): Used by Alembic migrations (psycopg2 driver)

### Database Session Management

**Dependency Pattern** (`get_db()`):
- One session per request
- Automatic transaction management
- Auto-commit on success, auto-rollback on error
- Proper cleanup even on exceptions

### Data Models

**Base Class**:
- `DeclarativeBase` from SQLAlchemy 2.0
- All models inherit from custom `Base` class

**Current Models**:
- **User**: id (PK), email (unique), first_name, last_name, hashed_password, is_active, created_at

**Typed Mappings**:
Uses `Mapped[type]` annotations for type safety and IDE support.

### Migrations (Alembic)

**Configuration**:
- **Script location**: `migrations/` directory
- **Database URL**: Dynamically set from settings in `migrations/env.py`
- **Target metadata**: Imported from `src.db.Base.metadata`
- **Offline mode**: Supported for SQL script generation
- **Online mode**: Default, uses database connection

**Current Migrations**:
1. `0620bbb0f141` - Initial migration setup
2. `d34add583c74` - Created users table

**Commands**:
- `poetry run alembic revision --autogenerate -m "message"` - Generate new migration
- `poetry run alembic upgrade head` - Apply all pending migrations
- `poetry run alembic downgrade -1` - Rollback one migration
- `poetry run alembic current` - Show current revision
- `poetry run alembic history` - Show migration history

**Exclusions**:
Migration files in `migrations/versions/` are excluded from Black, Ruff, and MyPy via pre-commit hooks.

---

## Exception Handling

### Exception Hierarchy

```
Exception (Python built-in)
└── AppError (src/core/exceptions.py)
    └── Auth Module Exceptions (src/auth/exceptions.py)
        ├── InvalidCredentialsError (401, AUTH_INVALID_CREDENTIALS)
        ├── TokenExpiredError (401, AUTH_TOKEN_EXPIRED)
        ├── InvalidTokenError (401, AUTH_INVALID_TOKEN)
        ├── UserInactiveError (403, AUTH_USER_INACTIVE)
        ├── PermissionDeniedError (403, AUTH_PERMISSION_DENIED)
        ├── UserNotFoundError (404, AUTH_USER_NOT_FOUND)
        └── UserAlreadyExistsError (409, AUTH_USER_ALREADY_EXISTS)
```

### Base Exception (AppError)

**Attributes**:
- `status_code` (int) - HTTP status code (default: 400)
- `error_code` (str) - Machine-readable error identifier
- `message` (str) - Human-readable error message
- `errors` (list[dict] | None) - Additional error details

**Response Format** (ErrorResponse):
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "errors": [...]  // optional
}
```

### Global Exception Handlers

Registered in `src/core/exceptions.py`:

1. **AppError Handler** - Catches custom domain exceptions, returns structured JSON
2. **HTTPException Handler** - Catches Starlette HTTP exceptions
3. **RequestValidationError Handler** - Catches Pydantic validation errors (422)
4. **RateLimitExceeded Handler** - Catches SlowAPI rate limit violations (429)
5. **Generic Exception Handler** - Catch-all for unhandled exceptions (500)

All handlers log appropriately and return consistent JSON error responses.

---

## Configuration Management

### Pydantic Settings

**Implementation**: `src/core/config.py` uses `BaseSettings` from `pydantic-settings`

**Configuration Hierarchy** (priority order):
1. Environment variables (highest)
2. `.env` file
3. Default values in code (lowest)

**Settings Class Configuration**:
- `env_file = ".env"` - Read from .env file
- `env_file_encoding = "utf-8"` - UTF-8 encoding
- `case_sensitive = False` - Case-insensitive environment variables
- `extra = "ignore"` - Ignore unknown environment variables

### Configuration Categories

**Server Settings**:
- `HOST` (default: "localhost") - Server bind host
- `PORT` (default: 8000) - Server bind port
- `ENVIRONMENT` (default: "development") - Literal["development", "production"]

**Rate Limiting**:
- `RATE_LIMIT` (default: "1/second") - Format: "amount/period"

**Database Settings**:
- `DB_USER` (default: "postgres") - Database username
- `DB_PASSWORD` (default: "1234") - Database password
- `DB_HOST` (default: "localhost") - Database host
- `DB_PORT` (default: 5432) - Database port
- `DB_NAME` (default: "datamodelchat") - Database name

**JWT Settings**:
- `JWT_SECRET_KEY` (default: "myjwtsecretkey") - **Change in production!**
- `JWT_ALGORITHM` (default: "HS256") - JWT signing algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30) - Token TTL

**Computed Properties**:
- `database_url` - PostgreSQL+asyncpg connection string
- `database_url_sync` - PostgreSQL+psycopg2 connection string

### Security Best Practices

- `.env` is gitignored
- `.env.example` provided as template
- No sensitive defaults (change `JWT_SECRET_KEY` in production)
- Configuration validation via Pydantic

---

## Logging System

### Configuration (`src/core/logging.py`)

**Log Directory**: `logs/` (created automatically)

**Log File Naming**: `YYYYMMDD-HHMMSS.log` (timestamp-based)

**Log Format**: `[timestamp] [logger_name] [level] message`

**Handlers**:
1. **StreamHandler** - Console output (stdout)
2. **FileHandler** - File output in `logs/` directory

**Logging Levels**:
- **Development**: DEBUG (verbose logging)
- **Production**: WARNING (errors and warnings only)

### Logged Events

**ProcessTimeMiddleware** logs:
- **INFO**: Successful requests with `METHOD PATH - STATUS - DURATION`
- **ERROR**: Failed requests with `METHOD PATH - Failed - DURATION`

**Exception Handlers** log:
- **WARNING**: AppError, HTTPException, validation errors, rate limits
- **ERROR**: Unhandled exceptions with stack traces

**Authentication** logs:
- **WARNING**: Invalid credentials, expired tokens, validation failures

### Per-Module Loggers

Each module uses `logger = logging.getLogger(__name__)` for granular control.

---

## Dependency Management (Poetry)

### Poetry Configuration

**Project Metadata** (`[project]` table in `pyproject.toml`):
- Uses **PEP 621** standard format
- `package-mode = false` - Not a distributable package
- `requires-python = ">=3.12,<3.13"` - Python version constraint

**Build System** (`[build-system]`):
- `poetry-core>=2.0.0,<3.0.0` as build backend
- Follows **PEP 517** standard

**Dependency Groups**:
- **Default group**: Production dependencies (runtime required)
- **Dev group** (`[dependency-groups].dev`): Development-only dependencies

### Dependency Specification

**Version Constraints**:
- Uses `>=min,<max` format for compatibility ranges
- Uses `==version` for pinned versions (e.g., bcrypt)
- Extras specified with `[extra]` notation (e.g., `uvicorn[standard]`)

### Poetry Commands

**Installation**:
- `poetry install` - Install all dependencies (including dev)
- `poetry install --without dev` - Install production only
- `poetry install --sync` - Remove unlisted packages

**Dependency Management**:
- `poetry add package` - Add production dependency
- `poetry add --group dev package` - Add dev dependency
- `poetry remove package` - Remove dependency
- `poetry update` - Update dependencies to latest compatible versions

**Lock File**:
- `poetry.lock` - Locked versions for reproducible installs
- Auto-updated on dependency changes
- Committed to version control

**Virtual Environment**:
- `poetry shell` - Activate virtualenv
- `poetry run command` - Run command in virtualenv

---

## Code Quality (Pre-commit)

### Pre-commit Hooks Configuration

**Hook Repositories** (`.pre-commit-config.yaml`):

1. **pre-commit-hooks** (v5.0.0):
   - `trailing-whitespace` - Remove trailing whitespace
   - `end-of-file-fixer` - Ensure files end with newline
   - `check-yaml` - Validate YAML syntax
   - `debug-statements` - Prevent debug statements in commits

2. **Black** (24.8.0):
   - Code formatter with Python 3.12 target
   - Excludes `migrations/versions/` directory
   - Opinionated, zero-config formatting

3. **Ruff** (v0.7.4):
   - Fast Python linter
   - `--fix` flag for auto-fixable issues
   - Excludes `migrations/versions/` directory

4. **MyPy** (v1.11.2):
   - Static type checker
   - Excludes `migrations/versions/` directory

### Usage

**Installation**:
```bash
poetry run pre-commit install  # Install git hooks
```

**Manual Execution**:
```bash
poetry run pre-commit run --all-files  # Run all hooks on all files
poetry run black src/                  # Format specific directory
poetry run ruff check src/             # Lint specific directory
poetry run mypy src/                   # Type check specific directory
```

**Auto-execution**:
Hooks run automatically on `git commit`, preventing commits with issues.

---

## API Documentation

### Auto-Generated Documentation

FastAPI provides interactive API documentation out-of-the-box:

**Swagger UI** - `http://localhost:8000/docs`
- Interactive API explorer
- Try endpoints directly in browser
- View request/response schemas

**ReDoc** - `http://localhost:8000/redoc`
- Alternative documentation UI
- Better for reading and printing

**OpenAPI Schema** - `http://localhost:8000/openapi.json`
- Machine-readable API specification
- OpenAPI 3.1.0 format

### Schema Generation

Documentation is auto-generated from:
- Python type hints
- Pydantic models
- Route decorators (`@router.get`, `response_model`, `status_code`)
- Docstrings (if provided)

---

## Health Checks

### Endpoints

**Root** (`GET /`):
- Returns `{"message": "Hello World"}`
- Basic liveness check

**Health Check** (`GET /health`):
- Database connectivity test
- Uptime tracking
- Version information
- Response format:
  ```json
  {
    "status": "ok" | "degraded",
    "uptime_seconds": 123.456,
    "version": "0.1.0",
    "db_status": "connected" | "disconnected"
  }
  ```

### Implementation Details

- Database check executes `SELECT 1` query
- Non-blocking async database check
- Version detection from package metadata (falls back to "0.1.0")
- Uptime calculated from server start time

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd data-model-chat-server

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Set up pre-commit hooks
poetry run pre-commit install

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run python -m src.main
```

### Development Server

**Command**: `poetry run python -m src.main`

**Features**:
- Auto-reload on code changes (development mode)
- Watches `src/` directory
- Binds to configured host:port (default: localhost:8000)
- DEBUG-level logging in development

---

## Summary

The **Data Model Chat Server** currently provides:

### ✅ Implemented Features

- **Authentication System**: JWT-based auth with registration, login, user management
- **Database Layer**: Async SQLAlchemy with connection pooling and migrations
- **API Framework**: FastAPI with automatic documentation
- **Configuration**: Environment-based settings with validation
- **Logging**: Structured logging with file and console output
- **Middleware**: CORS, rate limiting, request timing
- **Exception Handling**: Centralized error handling with structured responses
- **Code Quality**: Pre-commit hooks with formatting, linting, type checking
- **Health Checks**: Database connectivity and uptime monitoring

### 📚 Documentation

- **ARCHITECTURE.md**: This file - current system architecture
- **ROADMAP.md**: Future development phases and plans

---

**Version**: 1.2
**Last Updated**: 2025-12-08
**Status**: Production-ready authentication and infrastructure
