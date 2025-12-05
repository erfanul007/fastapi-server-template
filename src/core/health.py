from fastapi import APIRouter
from pydantic import BaseModel
from importlib.metadata import version, PackageNotFoundError
import time

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


@router.get("/", response_model=RootResponse)
async def read_root():
    return RootResponse(message="Hello World")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        uptime_seconds=round(time.time() - START_TIME, 3),
        version=APP_VERSION,
    )
