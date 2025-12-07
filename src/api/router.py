from fastapi import APIRouter

from src.auth import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
