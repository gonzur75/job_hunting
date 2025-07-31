
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.database import get_db
from app.crud.user import get_user_by_email, create_user
from app.models import User
from app.schemas.user import UserOut, UserCreate

router = APIRouter(prefix="/auth", tags=["auth", "users"])

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        user_in: Annotated[UserCreate, Body()],
        db: Annotated[AsyncSession,Depends(get_db)],
):
    existing = await get_user_by_email(user_in.email, db)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registred")
    user = await create_user(db, user_in)
    return user
