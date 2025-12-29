import logging
from typing import Any

from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError, WebSocketRequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

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


def app_error_handler(request: Request | WebSocket, exc: AppError):
    path = request.url.path if isinstance(request, (Request, WebSocket)) else "unknown"
    method = request.method if isinstance(request, Request) else "WEBSOCKET"

    logger.warning(
        "AppError [%s] %s %s: %s",
        exc.error_code,
        method,
        path,
        exc.message,
    )

    if isinstance(request, WebSocket):
        # We cannot return a JSONResponse to a WebSocket
        # The connection will likely be closed by the exception anyway
        return None

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
            detail="Request validation failed", errors=exc.errors()
        ).model_dump(exclude_none=True),
    )


def websocket_validation_exception_handler(
    request: WebSocket, exc: WebSocketRequestValidationError
):
    logger.warning(
        "WebSocket validation error on %s: %s",
        request.url.path,
        exc.errors(),
    )
    # No response can be sent; connection is closed by FastAPI
    return None


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
            detail=f"Rate limit exceeded: {exc}", error_code="RATE_LIMIT_EXCEEDED"
        ).model_dump(exclude_none=True),
    )


def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Internal server error").model_dump(
            exclude_none=True
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(
        WebSocketRequestValidationError, websocket_validation_exception_handler
    )
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
