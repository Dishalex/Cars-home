from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the FastAPI application."""

    DB_URL: str = "postgresql+asyncpg://user:password@localhost:5432/db"
    TG_TOKEN: str = "token"
    ADMINS: dict = {"admin": 12345678}

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"  # noqa
    )


config = Settings()
