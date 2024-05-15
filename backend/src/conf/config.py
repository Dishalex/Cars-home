from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the FastAPI application."""

    DB_URL: str = "postgresql+asyncpg://user:password@localhost:5432/db"
    SECRET_KEY_JWT: str = "secret"
    ALGORITHM: str = "HS256"
    CLD_NAME: str = "cloud_name"
    CLD_API_KEY: int = 12345678
    CLD_API_SECRET: str = "api_secret"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"  # noqa
    )


config = Settings()
