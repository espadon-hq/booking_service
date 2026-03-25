"""Спільні фікстури для всіх тестів проекту."""

from datetime import date, timedelta

import pytest
from booking_service.models import Hotel, Room, User


@pytest.fixture
def sample_hotel() -> Hotel:
    """Тестовий готель."""
    return Hotel(
        id=1,
        name="Test Hotel",
        city="Київ",
        address="вул. Тестова, 1",
        stars=3,
    )


@pytest.fixture
def sample_room() -> Room:
    """Тестова кімната."""
    return Room(
        id=1,
        hotel_id=1,
        number="101",
        room_type="double",
        price_per_night=1000.0,
        capacity=2,
    )


@pytest.fixture
def sample_user() -> User:
    """Тестовий користувач."""
    return User(
        id=1,
        name="Тест Користувач",
        email="test@example.com",
        phone="+380991234567",
    )


@pytest.fixture
def future_dates() -> tuple[date, date]:
    """Коректні майбутні дати — заїзд завтра, виїзд через 3 дні."""
    today = date.today()
    return today + timedelta(days=1), today + timedelta(days=4)