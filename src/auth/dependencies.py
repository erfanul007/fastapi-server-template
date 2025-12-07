from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import get_db
from src.auth.security import decode_jwt_token
from src.auth.models import User
from src.auth.schemas import UserRead, TokenData
from src.auth.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    token_data = decode_jwt_token(token)
    if token_data.token_type != "access":
        raise InvalidTokenError()
    return token_data

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    token_data = decode_jwt_token(token)

    if token_data.token_type != "access":
        raise InvalidTokenError()

    stmt = select(User).where(User.id == token_data.user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise InvalidTokenError("User not found")

    if not user.is_active:
        raise InvalidTokenError("User is inactive")

    return user

CurrentToken = Annotated[TokenData, Depends(get_token_data)]
CurrentUser = Annotated[UserRead, Depends(get_current_user)]