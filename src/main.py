import logging

from fastapi import FastAPI

from src.api import api_router
from src.core import (
    register_exception_handlers,
    register_middlewares,
    settings,
    setup_logging,
)
from src.core.health import router as health_router

setup_logging()
logger = logging.getLogger(__name__)

logger.info(
    f"Starting server on {settings.host}:{settings.port} [{settings.environment}]"
)

app = FastAPI(title="FastAPI Server Template")

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
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
