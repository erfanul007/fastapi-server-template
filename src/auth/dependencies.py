import logging
from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db

from .exceptions import InvalidTokenError
from .models import User
from .schemas import TokenData, UserRead
from .security import decode_jwt_token
from .service import get_user_by_id

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    token_data = decode_jwt_token(token)
    if token_data.token_type != "access":
        raise InvalidTokenError()
    return token_data


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token_data = decode_jwt_token(token)

    if token_data.token_type != "access":
        raise InvalidTokenError()

    user = await get_user_by_id(db, token_data.user_id)

    if not user:
        raise InvalidTokenError("User not found")

    if not user.is_active:
        raise InvalidTokenError("User is inactive")

    return user


async def require_ws_user(token: str = Query(...)) -> TokenData:
    token_data = decode_jwt_token(token)
    if token_data.token_type != "access":
        raise InvalidTokenError()
    return token_data


ValidToken = Annotated[TokenData, Depends(get_token_data)]
AuthenticatedUser = Annotated[UserRead, Depends(get_current_user)]
WSValidToken = Annotated[TokenData, Depends(require_ws_user)]
