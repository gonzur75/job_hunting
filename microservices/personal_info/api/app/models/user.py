from sqlalchemy import Column, Integer, String

from app.core.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

