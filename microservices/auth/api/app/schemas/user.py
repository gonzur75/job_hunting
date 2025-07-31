import enum
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr, field_serializer, StringConstraints

class UserRole(str, enum.Enum):
    user = 'user'
    admin = 'admin'

class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(description="User email address")]
    full_name: Annotated[str | None, Field(description="User full name", default=None)]

    @field_serializer("email")
    def serialize_email(self, email: EmailStr) -> str:
        return str(email)

class UserCreate(UserBase):

    password: Annotated[
        str,
        Field(min_length=8, description="User password, minimum 8 characters long."),
    ]
    model_config = ConfigDict(
        from_attributes=True,
    )

class UserOut(UserBase):
    id: int = Field(description="User ID")
    is_active: bool = Field(description="User is active")
    is_verified: bool = Field(description="User is verified")
    role: UserRole = Field(description="User role")
    created_at: datetime = Field(description="Account creation timestamp")


    model_config = ConfigDict(
        from_attributes=True,
    )

class UserInDB(UserOut):
    hashed_password: str = Field(description="Hashed user password(only for internal use)")