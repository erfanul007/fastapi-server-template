from fastapi import FastAPI
from src.core.config import settings
from src.core.logging import setup_logging
from src.core.exceptions import register_exception_handlers
from src.core.middleware import register_middlewares
from src.core.health import router as health_router
from src.auth.router import router as auth_router
import logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info(f"Starting server on {settings.host}:{settings.port} [{settings.environment}]")

app = FastAPI(title="Data Model Chat Server")

register_middlewares(app)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.environment == "development"),
        reload_dirs=["src"],
    )
