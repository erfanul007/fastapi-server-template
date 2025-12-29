from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import ErrorResponse
from src.db import get_db

from .dependencies import AuthenticatedUser, ValidToken
from .schemas import LoginResponse, UserCreate, UserLogin, UserRead
from .service import get_all_users, login_user, register_user

router = APIRouter()


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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    payload = UserLogin(email=form_data.username, password=form_data.password)
    return await login_user(db, payload)


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
)
async def get_current_user(
    current_user: AuthenticatedUser,
):
    return current_user


@router.get(
    "/users",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    responses={401: {"model": ErrorResponse}},
)
async def get_users(_token_data: ValidToken, db: AsyncSession = Depends(get_db)):
    return await get_all_users(db)
