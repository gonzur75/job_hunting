from fastapi import APIRouter
from app.routers.user import router as user_router

routers: list[APIRouter] = [
    user_router,
]