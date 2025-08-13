from functools import lru_cache
import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables.

    Note:
    - For production, set SECRET_KEY and DATABASE_URL using environment variables.
    - You can prepare a .env file using the provided .env.example to set these.
    """

    APP_NAME: str = Field(default="Notes Backend API", description="Application display name.")
    APP_DESCRIPTION: str = Field(
        default="Backend service for handling note data, user authentication, and business logic.",
        description="Description for OpenAPI docs.",
    )
    APP_VERSION: str = Field(default="1.0.0", description="Application version for OpenAPI docs.")

    # Security
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION"),
        description="Secret key for signing JWT tokens.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        description="JWT access token expiration in minutes.",
    )
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"), description="JWT algorithm to use.")

    # CORS
    CORS_ALLOW_ORIGINS: str = Field(
        default=os.getenv("CORS_ALLOW_ORIGINS", "*"),
        description="Comma-separated list of allowed origins for CORS.",
    )

    # Database
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite:///./notes.db"),
        description="Database connection URL.",
    )


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings loaded from environment variables."""
    return Settings()
