from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import DateTime


class UserSchema(BaseModel):
    """Pydantic model for validating incoming user registration data."""
    full_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=20)
    phone_number: str = Field(min_length=10, max_length=20)
    telegram_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Pydantic model for validating incoming user data for updating."""
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    phone_number: str | None = None
    telegram_id: int | None = None


class UserResponse(BaseModel):
    """Pydantic model for serializing user data in responses."""
    full_name: str
    email: EmailStr
    phone_number: str
    telegram_id: int | None


class HistoryResponse(BaseModel):
    entry_time: DateTime
    exit_time: Optional[DateTime]
    parking_time: Optional[float]
    cost: float
    paid: bool
    car: str
