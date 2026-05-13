"""Підключення до БД, конфігурація та ORM моделі."""
from datetime import date, datetime, timezone

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import (
    CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


# ── Конфігурація ──────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """Налаштування застосунку — зчитує змінні з .env."""
    app_name: str = "Booking Service"
    app_version: str = "0.0.1"
    debug: bool = False
    database_url: str = "postgresql://booking_user:booking_pass@localhost:5432/booking_db"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# ── Підключення ───────────────────────────────────────────────────────────────

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Базовий клас для всіх SQLAlchemy моделей."""
    pass


def get_db():
    """Генератор сесії БД для FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Створює всі таблиці в БД якщо вони ще не існують."""
    Base.metadata.create_all(bind=engine)


# ── ORM Моделі ────────────────────────────────────────────────────────────────

class Hotel(Base):
    """Модель готелю."""
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")

    __table_args__ = (CheckConstraint("stars >= 1 AND stars <= 5", name="stars_range"),)

    def __repr__(self):
        return f"<Hotel id={self.id} name={self.name!r} city={self.city!r}>"


class Room(Base):
    """Модель кімнати готелю."""
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(Integer, ForeignKey("hotels.id"), nullable=False)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Room id={self.id} number={self.number!r} hotel_id={self.hotel_id}>"


class User(Base):
    """Модель користувача."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"


class Booking(Base):
    """Модель бронювання."""
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in: Mapped[date] = mapped_column(DateTime, nullable=False)
    check_out: Mapped[date] = mapped_column(DateTime, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")

    def __repr__(self):
        return f"<Booking id={self.id} room_id={self.room_id} status={self.status!r}>"
