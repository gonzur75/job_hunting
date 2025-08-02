from pydantic import EmailStr

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models import User
from app.schemas.user import UserCreate


async def get_user_by_email(email: EmailStr, db: AsyncSession) -> User | None:
    result =  await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:

    db_user = User(
        email = user_in.email,
        hashed_password = get_password_hash(user_in.password),
        full_name = user_in.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()