import logging
from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
    errors: list[dict[str, Any]] | None = None


class AppError(Exception):
    """
    Base application exception.
    Domain modules should inherit this and override
    the `status_code`, `error_code`, and `message` attributes.
    """
    status_code: int = 400
    error_code: str = "APP_ERROR"
    message: str = "Application error"
    errors: list[dict[str, Any]] | None = None

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        if errors is not None:
            self.errors = errors

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            detail=self.message,
            error_code=self.error_code,
            errors=self.errors,
        )


def app_error_handler(request: Request, exc: AppError):
    logger.warning(
        "AppError [%s] %s %s: %s",
        exc.error_code,
        request.method,
        request.url.path,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump(exclude_none=True),
    )


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        "HTTP error %s on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail)).model_dump(exclude_none=True),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Request validation failed",
            errors=exc.errors()
        ).model_dump(exclude_none=True),
    )


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(
        "Rate limit exceeded on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            detail=f"Rate limit exceeded: {exc}",
            error_code="RATE_LIMIT_EXCEEDED"
        ).model_dump(exclude_none=True),
    )


def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Internal server error").model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
