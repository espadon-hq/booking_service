"""Конфігурація застосунку — зчитує змінні з .env файлу."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Налаштування застосунку."""

    app_name: str = "Booking Service"
    app_version: str = "0.0.1"
    debug: bool = False
    database_url: str = (
        "postgresql://booking_user:booking_pass@localhost:5432/booking_db"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()