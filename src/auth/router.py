from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginResponse, UserCreate, UserLogin, UserRead
from src.db.database import get_db
from src.core.exceptions import ErrorResponse
from src.auth.service import register_user, login_user, get_all_users
from src.auth.dependencies import CurrentToken, CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await register_user(db, payload)

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    return await login_user(db, payload)

@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
)
async def get_current_user(
    current_user: CurrentUser,
):
    return current_user

@router.get(
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
)
async def get_users(
    token_data: CurrentToken,
    db: AsyncSession = Depends(get_db)
):
    return await get_all_users(db)
