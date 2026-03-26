"""Модуль підключення до бази даних PostgreSQL через SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from booking_service.config import settings

# Створюємо рушій підключення до PostgreSQL
engine = create_engine(
    settings.database_url,
    # Розмір пулу підключень — кількість одночасних з'єднань
    pool_size=5,
    # Додаткові підключення понад pool_size при пікових навантаженнях
    max_overflow=10,
    # Час очікування вільного підключення з пулу (секунди)
    pool_timeout=30,
    # Перевіряти з'єднання перед використанням — захист від обривів
    pool_pre_ping=True,
)

# Фабрика сесій для роботи з БД
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовий клас для всіх SQLAlchemy моделей.

    Всі моделі успадковуються від цього класу —
    це дозволяє створити таблиці через Base.metadata.create_all().
    """
    pass


def get_db():
    """Генератор сесії БД для використання як залежність у FastAPI.

    Гарантує що сесія завжди закривається після запиту.

    Yields:
        Session: активна сесія SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Створює всі таблиці в БД якщо вони ще не існують."""
    # Імпортуємо моделі щоб SQLAlchemy знав про них
    from booking_service import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)