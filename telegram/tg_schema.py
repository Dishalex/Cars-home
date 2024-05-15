from pydantic import BaseModel, EmailStr


class UserUpdate(BaseModel):
    """Pydantic model for validating incoming user data for updating."""
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    phone_number: str | None = None
    telegram_id: int | None = None
