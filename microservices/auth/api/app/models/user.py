import enum
import datetime as dt
from pydantic import EmailStr

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import Boolean, Enum, DateTime

from app.core.database import Base

class UserRole(enum.Enum):
    user = 'user'
    admin = 'admin'

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[EmailStr] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now(),
                                            onupdate=func.now(), nullable=False)

    def __repr__(self):
        return (f"User(email={self.email!r}, full_name={self.full_name!r}), role={self.role!r},"
                f"is_active={self.is_active!r}, is_verified={self.is_verified!r}"
                )

    def __str__(self):
        return f'User {self.id}: {self.email} ({self.role})'