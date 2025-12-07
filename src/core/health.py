from fastapi import APIRouter
from pydantic import BaseModel
from importlib.metadata import version, PackageNotFoundError
import time
from src.db.database import async_engine
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

router = APIRouter()

START_TIME = time.time()

try:
    APP_VERSION = version("data-model-chat-server")
except PackageNotFoundError:
    APP_VERSION = "0.1.0"

class RootResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str
    db_status: str | None = None


@router.get("/", response_model=RootResponse)
async def read_root():
    return RootResponse(message="Hello World")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    status = "ok"
    uptime = round(time.time() - START_TIME, 3)
    db_status = None
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except SQLAlchemyError:
        status = "degraded"
        db_status = "disconnected"


    return HealthResponse(
        status=status,
        uptime_seconds=uptime,
        version=APP_VERSION,
        db_status=db_status,
    )
