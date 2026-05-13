"""Pydantic схеми для валідації даних API.

Лаб 5 — схеми для вхідних та вихідних даних REST API.
"""

from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


# ── Hotel ─────────────────────────────────────────────────────────────────────


class HotelCreate(BaseModel):
    """Схема для створення готелю."""

    name: str = Field(..., min_length=2, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=300)
    stars: int = Field(..., ge=1, le=5)
    description: str = Field(default="", max_length=2000)


class HotelUpdate(BaseModel):
    """Схема для оновлення готелю — всі поля необов'язкові."""

    name: str | None = Field(None, min_length=2, max_length=200)
    city: str | None = Field(None, min_length=2, max_length=100)
    address: str | None = Field(None, min_length=5, max_length=300)
    stars: int | None = Field(None, ge=1, le=5)
    description: str | None = Field(None, max_length=2000)


class HotelOut(BaseModel):
    """Схема для відповіді API — готель."""

    id: int
    name: str
    city: str
    address: str
    stars: int
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Room ──────────────────────────────────────────────────────────────────────


class RoomCreate(BaseModel):
    """Схема для створення кімнати."""

    number: str = Field(..., min_length=1, max_length=20)
    room_type: str = Field(..., min_length=2, max_length=50)
    price_per_night: float = Field(..., gt=0)
    capacity: int = Field(default=2, ge=1, le=20)


class RoomOut(BaseModel):
    """Схема для відповіді API — кімната."""

    id: int
    hotel_id: int
    number: str
    room_type: str
    price_per_night: float
    capacity: int

    model_config = {"from_attributes": True}


class RoomAvailabilityOut(RoomOut):
    """Схема кімнати з інформацією про доступність."""

    available: bool
    total_price: float | None = None
    nights: int | None = None


# ── User ──────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Схема для створення користувача."""

    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(default="", max_length=50)


class UserOut(BaseModel):
    """Схема для відповіді API — користувач."""

    id: int
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Booking ───────────────────────────────────────────────────────────────────


class BookingCreate(BaseModel):
    """Схема для створення бронювання."""

    user_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    check_in: date
    check_out: date

    def model_post_init(self, __context) -> None:
        """Перевіряє що дата виїзду пізніше дати заїзду."""
        if self.check_out <= self.check_in:
            raise ValueError("Дата виїзду повинна бути пізніше дати заїзду.")


class BookingOut(BaseModel):
    """Схема для відповіді API — бронювання."""

    id: int
    user_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingDetailOut(BookingOut):
    """Розширена схема бронювання з деталями готелю та кімнати."""

    hotel_name: str | None = None
    room_number: str | None = None
    nights: int | None = None


# ── Загальні схеми ────────────────────────────────────────────────────────────


class MessageOut(BaseModel):
    """Схема для простих повідомлень."""

    message: str


class AvailabilityRequest(BaseModel):
    """Схема запиту на перевірку доступності."""

    check_in: date
    check_out: date