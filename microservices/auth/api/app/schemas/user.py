import enum
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr

class UserRole(str, enum.Enum):
    user = 'user'
    admin = 'admin'

class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(description="User email address")]
    full_name: Annotated[str | None, Field(description="User full name", default=None)]

class UserCreate(UserBase):

    password: Annotated[
        str, constr(min_length=8),
        Field(description="User password, minimum 8 characters long."),
    ]

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