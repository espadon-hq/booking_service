"""Тести для репозиторію — перевірка операцій з БД.

Використовує SQLite in-memory БД для швидкого тестування
без необхідності запускати PostgreSQL.
"""

from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from booking_service import repository as repo
from booking_service.database import Base

# ── Фікстури ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def db():
    """Створює тимчасову SQLite in-memory БД для кожного тесту.

    Після тесту БД повністю видаляється — тести ізольовані.
    """
    # Використовуємо SQLite для тестів — не потребує PostgreSQL
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Створюємо всі таблиці
    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        # Видаляємо всі таблиці після тесту
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def hotel(db):
    """Створює тестовий готель в БД."""
    return repo.create_hotel(
        db,
        name="Test Hotel",
        city="Київ",
        address="вул. Тестова, 1",
        stars=4,
        description="Тестовий готель",
    )


@pytest.fixture
def room(db, hotel):
    """Створює тестову кімнату в БД."""
    return repo.create_room(
        db,
        hotel_id=hotel.id,
        number="101",
        room_type="double",
        price_per_night=1500.0,
        capacity=2,
    )


@pytest.fixture
def user(db):
    """Створює тестового користувача в БД."""
    return repo.create_user(
        db,
        name="Тест Користувач",
        email="test@example.com",
        phone="+380991234567",
    )


@pytest.fixture
def future_dates():
    """Повертає майбутні дати — заїзд завтра, виїзд через 4 дні."""
    today = date.today()
    return today + timedelta(days=1), today + timedelta(days=4)


# ── Hotel ─────────────────────────────────────────────────────────────────────


class TestHotelRepository:
    """Тести для операцій з готелями."""

    def test_create_hotel(self, db):
        """Готель успішно створюється в БД."""
        hotel = repo.create_hotel(
            db, "Grand Hotel", "Одеса", "вул. Морська, 1", 5
        )
        assert hotel.id is not None
        assert hotel.name == "Grand Hotel"
        assert hotel.city == "Одеса"
        assert hotel.stars == 5

    def test_get_hotel_by_id(self, db, hotel):
        """get_hotel_by_id повертає коректний готель."""
        found = repo.get_hotel_by_id(db, hotel.id)
        assert found is not None
        assert found.id == hotel.id
        assert found.name == hotel.name

    def test_get_hotel_by_id_not_found(self, db):
        """get_hotel_by_id повертає None для неіснуючого id."""
        assert repo.get_hotel_by_id(db, 9999) is None

    def test_get_all_hotels(self, db, hotel):
        """get_all_hotels повертає список з усіма готелями."""
        hotels = repo.get_all_hotels(db)
        assert len(hotels) >= 1
        assert any(h.id == hotel.id for h in hotels)

    def test_get_hotels_by_city(self, db, hotel):
        """get_hotels_by_city повертає готелі у вказаному місті."""
        hotels = repo.get_hotels_by_city(db, "Київ")
        assert any(h.id == hotel.id for h in hotels)

    def test_get_hotels_by_city_case_insensitive(self, db, hotel):
        """Фільтрація за містом не залежить від регістру."""
        hotels = repo.get_hotels_by_city(db, "київ")
        assert any(h.id == hotel.id for h in hotels)

    def test_update_hotel(self, db, hotel):
        """update_hotel оновлює поля готелю."""
        updated = repo.update_hotel(db, hotel.id, name="New Name", stars=5)
        assert updated.name == "New Name"
        assert updated.stars == 5

    def test_update_hotel_not_found(self, db):
        """update_hotel повертає None для неіснуючого id."""
        assert repo.update_hotel(db, 9999, name="Test") is None

    def test_delete_hotel(self, db, hotel):
        """delete_hotel видаляє готель з БД."""
        result = repo.delete_hotel(db, hotel.id)
        assert result is True
        assert repo.get_hotel_by_id(db, hotel.id) is None

    def test_delete_hotel_not_found(self, db):
        """delete_hotel повертає False для неіснуючого id."""
        assert repo.delete_hotel(db, 9999) is False


# ── Room ──────────────────────────────────────────────────────────────────────


class TestRoomRepository:
    """Тести для операцій з кімнатами."""

    def test_create_room(self, db, hotel):
        """Кімната успішно створюється в БД."""
        room = repo.create_room(
            db,
            hotel_id=hotel.id,
            number="202",
            room_type="suite",
            price_per_night=3000.0,
            capacity=3,
        )
        assert room.id is not None
        assert room.number == "202"
        assert room.hotel_id == hotel.id

    def test_get_rooms_by_hotel(self, db, hotel, room):
        """get_rooms_by_hotel повертає кімнати готелю."""
        rooms = repo.get_rooms_by_hotel(db, hotel.id)
        assert len(rooms) >= 1
        assert any(r.id == room.id for r in rooms)

    def test_get_room_by_id(self, db, room):
        """get_room_by_id повертає коректну кімнату."""
        found = repo.get_room_by_id(db, room.id)
        assert found is not None
        assert found.id == room.id

    def test_get_room_by_id_not_found(self, db):
        """get_room_by_id повертає None для неіснуючого id."""
        assert repo.get_room_by_id(db, 9999) is None

    def test_delete_room(self, db, room):
        """delete_room видаляє кімнату з БД."""
        result = repo.delete_room(db, room.id)
        assert result is True
        assert repo.get_room_by_id(db, room.id) is None

    def test_available_rooms_empty_bookings(self, db, hotel, room, future_dates):
        """Кімната вільна якщо немає бронювань."""
        check_in, check_out = future_dates
        available = repo.get_available_rooms(db, hotel.id, check_in, check_out)
        assert any(r.id == room.id for r in available)


# ── User ──────────────────────────────────────────────────────────────────────


class TestUserRepository:
    """Тести для операцій з користувачами."""

    def test_create_user(self, db):
        """Користувач успішно створюється в БД."""
        user = repo.create_user(db, "Іван", "ivan@test.com", "+380991111111")
        assert user.id is not None
        assert user.email == "ivan@test.com"

    def test_create_user_duplicate_email(self, db, user):
        """Дублікат email викидає ValueError."""
        with pytest.raises(ValueError, match="вже існує"):
            repo.create_user(db, "Інший", user.email)

    def test_get_user_by_id(self, db, user):
        """get_user_by_id повертає коректного користувача."""
        found = repo.get_user_by_id(db, user.id)
        assert found is not None
        assert found.email == user.email

    def test_get_user_by_email(self, db, user):
        """get_user_by_email повертає коректного користувача."""
        found = repo.get_user_by_email(db, user.email)
        assert found is not None
        assert found.id == user.id

    def test_get_user_by_email_not_found(self, db):
        """get_user_by_email повертає None для неіснуючого email."""
        assert repo.get_user_by_email(db, "nobody@test.com") is None

    def test_get_all_users(self, db, user):
        """get_all_users повертає список з усіма користувачами."""
        users = repo.get_all_users(db)
        assert any(u.id == user.id for u in users)


# ── Booking ───────────────────────────────────────────────────────────────────


class TestBookingRepository:
    """Тести для операцій з бронюваннями."""

    def test_create_booking(self, db, user, room, future_dates):
        """Бронювання успішно створюється в БД."""
        check_in, check_out = future_dates
        booking = repo.create_booking(
            db,
            user_id=user.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            total_price=4500.0,
        )
        assert booking.id is not None
        assert booking.status == "confirmed"
        assert booking.user_id == user.id
        assert booking.room_id == room.id

    def test_get_booking_by_id(self, db, user, room, future_dates):
        """get_booking_by_id повертає коректне бронювання."""
        check_in, check_out = future_dates
        booking = repo.create_booking(
            db, user.id, room.id, check_in, check_out, 3000.0
        )
        found = repo.get_booking_by_id(db, booking.id)
        assert found is not None
        assert found.id == booking.id

    def test_get_booking_by_id_not_found(self, db):
        """get_booking_by_id повертає None для неіснуючого id."""
        assert repo.get_booking_by_id(db, 9999) is None

    def test_get_bookings_by_user(self, db, user, room, future_dates):
        """get_bookings_by_user повертає бронювання користувача."""
        check_in, check_out = future_dates
        booking = repo.create_booking(
            db, user.id, room.id, check_in, check_out, 3000.0
        )
        bookings = repo.get_bookings_by_user(db, user.id)
        assert any(b.id == booking.id for b in bookings)

    def test_cancel_booking(self, db, user, room, future_dates):
        """cancel_booking змінює статус на 'cancelled'."""
        check_in, check_out = future_dates
        booking = repo.create_booking(
            db, user.id, room.id, check_in, check_out, 3000.0
        )
        cancelled = repo.cancel_booking(db, booking.id)
        assert cancelled.status == "cancelled"

    def test_cancel_booking_not_found(self, db):
        """cancel_booking повертає None для неіснуючого id."""
        assert repo.cancel_booking(db, 9999) is None

    def test_get_all_bookings(self, db, user, room, future_dates):
        """get_all_bookings повертає всі бронювання."""
        check_in, check_out = future_dates
        repo.create_booking(
            db, user.id, room.id, check_in, check_out, 3000.0
        )
        bookings = repo.get_all_bookings(db)
        assert len(bookings) >= 1