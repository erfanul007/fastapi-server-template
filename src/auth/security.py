import logging
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.core import settings

from .exceptions import InvalidTokenError, TokenExpiredError
from .schemas import TokenData

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token_data(user_id: int) -> TokenData:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    return TokenData(user_id=user_id, token_type="access", exp=exp)


def create_jwt_token(token_data: TokenData) -> str:
    json_data = token_data.model_dump()
    encoded_jwt = jwt.encode(
        json_data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_data = TokenData(**payload)
        return token_data
    except jwt.ExpiredSignatureError:
        logger.info("Token expired")
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        raise InvalidTokenError()
