from src.auth.models import User
from src.auth.schemas import LoginResponse, UserCreate, UserLogin, UserRead
from src.auth.security import get_password_hash, verify_password, create_access_token_data, create_jwt_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.exceptions import UserAlreadyExistsError, InvalidCredentialsError

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def register_user(db: AsyncSession, payload: UserCreate) -> UserRead:
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise UserAlreadyExistsError()

    user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user

async def login_user(db: AsyncSession, payload: UserLogin) -> LoginResponse:
    user = await get_user_by_email(db, payload.email)
    if not user:
        raise InvalidCredentialsError()
    if not verify_password(payload.password, user.hashed_password):
        raise InvalidCredentialsError()
    access_token = create_jwt_token(create_access_token_data(user.id))
    return LoginResponse(access_token=access_token)

async def get_all_users(db: AsyncSession) -> list[UserRead]:
    stmt = select(User)
    res = await db.execute(stmt)
    return res.scalars().all()
