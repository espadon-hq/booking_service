"""Конфігурація застосунку — зчитує змінні з .env файлу."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Налаштування застосунку.

    Всі значення автоматично зчитуються з .env файлу
    або змінних середовища.
    """

    # Інформація про застосунок
    app_name: str = "Booking Service"
    app_version: str = "0.0.1"
    debug: bool = False

    # Підключення до PostgreSQL — лише рядок підключення
    database_url: str = (
        "postgresql://booking_user:booking_pass@localhost:5432/booking_db"
    )

    class Config:
        """Налаштування Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ігноруємо зайві змінні з .env (POSTGRES_USER, POSTGRES_PASSWORD тощо)
        # Вони потрібні лише для docker-compose, не для Python
        extra = "ignore"


# Єдиний екземпляр налаштувань для всього застосунку
settings = Settings()