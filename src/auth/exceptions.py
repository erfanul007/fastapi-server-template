from src.core import AppError


class InvalidCredentialsError(AppError):
    status_code = 401
    error_code = "AUTH_INVALID_CREDENTIALS"
    message = "Invalid username or password"


class TokenExpiredError(AppError):
    status_code = 401
    error_code = "AUTH_TOKEN_EXPIRED"
    message = "Access token has expired"


class InvalidTokenError(AppError):
    status_code = 401
    error_code = "AUTH_INVALID_TOKEN"
    message = "Invalid or malformed access token"


class UserInactiveError(AppError):
    status_code = 403
    error_code = "AUTH_USER_INACTIVE"
    message = "User account is inactive"


class PermissionDeniedError(AppError):
    status_code = 403
    error_code = "AUTH_PERMISSION_DENIED"
    message = "You do not have permission to perform this action"


class UserNotFoundError(AppError):
    status_code = 404
    error_code = "AUTH_USER_NOT_FOUND"
    message = "User not found"


class UserAlreadyExistsError(AppError):
    status_code = 409
    error_code = "AUTH_USER_ALREADY_EXISTS"
    message = "User with this email already exists"
