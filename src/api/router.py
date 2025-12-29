from fastapi import APIRouter

from src.auth import auth_router
from src.realtime import ws_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(ws_router, prefix="/ws", tags=["ws"])
