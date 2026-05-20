from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    AUTO_CREATE_TABLES: bool = True

    # Redis cache
    REDIS_URL: str | None = None
    USER_CACHE_TTL_SECONDS: int = 300

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    # Email (verification)
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_PORT: int | None = None
    MAIL_SERVER: str | None = None
    MAIL_FROM_NAME: str = "Contacts API"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    # Cloudinary (avatars)
    CLOUDINARY_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # CORS
    # Comma-separated list, e.g. "http://localhost:3000,http://127.0.0.1:3000"
    CORS_ORIGINS: str = "*"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()

