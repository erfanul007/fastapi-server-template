from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from src.core.config import settings

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

async_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo= (settings.environment == 'development'),
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
