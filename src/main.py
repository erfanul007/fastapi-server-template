from fastapi import FastAPI

from src.core import (
    settings,
    setup_logging,
    register_exception_handlers,
    register_middlewares,
)
from src.core.health import router as health_router
from src.api import api_router
import logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info(
    f"Starting server on {settings.host}:{settings.port} [{settings.environment}]"
)

app = FastAPI(title="Data Model Chat Server")

register_middlewares(app)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.environment == "development"),
        reload_dirs=["src"],
    )
