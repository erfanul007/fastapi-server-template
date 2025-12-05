import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.core.config import settings

logger = logging.getLogger(__name__)


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.default_rate_limit]
)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    Minimal middleware to log processing time.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            
            logger.info(
                "%s %s - %s - %.4fs",
                request.method,
                request.url.path,
                response.status_code,
                process_time
            )
            return response
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                "%s %s - Failed - %.4fs",
                request.method,
                request.url.path,
                process_time
            )
            raise e


def register_middlewares(app: FastAPI) -> None:
    """
    Register all global middlewares and the Rate Limiter state.
    """
    
    app.state.limiter = limiter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(ProcessTimeMiddleware)
