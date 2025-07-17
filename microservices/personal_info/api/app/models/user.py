from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column


from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    social_links: Mapped[list["SocialLink"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )