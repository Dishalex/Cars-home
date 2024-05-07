# backend/src/schemas/user_schema.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from backend.src.entity.models import Role


class UserSchema(BaseModel):
    """Pydantic model for validating incoming user registration data."""
    full_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=20)
    phone_number: str = Field(min_length=10, max_length=20)
    telegram_id: str = Field(min_length=2, max_length=50)


class UserResponse(BaseModel):
    """Pydantic model for serializing user data in responses."""
    id: int = 1
    full_name: str
    email: EmailStr
    phone_number: str
    telegram_id: str
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Pydantic model for validating incoming user data for updating."""
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    phone_number: Optional[str]
    telegram_id: Optional[str]


class AnotherUsers(BaseModel):
    """Pydantic model for serializing simplified user data in responses."""
    full_name: str
    email: EmailStr
    phone_number: str
    telegram_id: str
    created_at: datetime


class TokenSchema(BaseModel):
    """Pydantic model for serializing JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
