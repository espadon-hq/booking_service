"""Тести для booking_service — бізнес-логіка, репозиторій, API."""
from datetime import date, timedelta
import pytest
from booking_service.models import Booking, Room
from booking_service.repository import (
    calculate_total_price, filter_hotels_by_city,
    filter_rooms_by_price, is_dates_valid, is_room_available,
)
from booking_service import repository as repo


# ── Бізнес-логіка ─────────────────────────────────────────────────────────────
# Тести чистих функцій без залежностей від БД

def test_calculate_total_price(sample_room, future_dates):
    """Ціна = price_per_night * кількість ночей (3 ночі = 3000 грн)."""
    check_in, check_out = future_dates
    assert calculate_total_price(sample_room, check_in, check_out) == 3000.0

def test_calculate_total_price_raises(sample_room):
    """Викидає ValueError якщо виїзд раніше заїзду."""
    today = date.today()
    with pytest.raises(ValueError):
        calculate_total_price(sample_room, today + timedelta(days=3), today + timedelta(days=1))

def test_is_dates_valid_future(future_dates):
    """Майбутні дати — валідні."""
    assert is_dates_valid(*future_dates) is True

def test_is_dates_valid_past():
    """Дата заїзду в минулому — невалідна."""
    yesterday = date.today() - timedelta(days=1)
    assert is_dates_valid(yesterday, date.today() + timedelta(days=2)) is False

def test_is_room_available_empty():
    """Кімната вільна якщо немає жодних бронювань."""
    today = date.today()
    assert is_room_available(1, today + timedelta(1), today + timedelta(4), []) is True

def test_is_room_available_overlap(future_dates):
    """Кімната зайнята якщо дати перетинаються з існуючим бронюванням."""
    check_in, check_out = future_dates
    booking = Booking(1, 1, 1, check_in, check_out, 3000.0, "confirmed")
    assert is_room_available(1, check_in, check_out, [booking]) is False

def test_is_room_available_cancelled(future_dates):
    """Скасоване бронювання не блокує кімнату."""
    check_in, check_out = future_dates
    booking = Booking(1, 1, 1, check_in, check_out, 3000.0, "cancelled")
    assert is_room_available(1, check_in, check_out, [booking]) is True

def test_filter_hotels_by_city(sample_hotel):
    """Фільтрація готелів за містом — без урахування регістру."""
    assert filter_hotels_by_city([sample_hotel], "київ") == [sample_hotel]
    assert filter_hotels_by_city([sample_hotel], "Одеса") == []

def test_filter_rooms_by_price(sample_room):
    """Фільтрація кімнат за максимальною ціною."""
    assert sample_room in filter_rooms_by_price([sample_room], 1500.0)
    assert filter_rooms_by_price([sample_room], 500.0) == []


# ── Репозиторій ───────────────────────────────────────────────────────────────
# Тести CRUD операцій через SQLite in-memory БД

def test_create_and_get_hotel(db):
    """Готель створюється і знаходиться за id."""
    hotel = repo.create_hotel(db, "Test", "Київ", "вул. 1", 4)
    assert repo.get_hotel_by_id(db, hotel.id).name == "Test"
    assert repo.get_hotel_by_id(db, 9999) is None  # неіснуючий id → None

def test_update_and_delete_hotel(db):
    """Готель оновлюється і видаляється з БД."""
    hotel = repo.create_hotel(db, "Test", "Київ", "вул. 1", 4)
    repo.update_hotel(db, hotel.id, name="Updated")
    assert repo.get_hotel_by_id(db, hotel.id).name == "Updated"
    repo.delete_hotel(db, hotel.id)
    assert repo.get_hotel_by_id(db, hotel.id) is None  # після видалення → None

def test_create_and_get_room(db, hotel):
    """Кімната створюється і знаходиться за id."""
    room = repo.create_room(db, hotel.id, "101", "double", 1500.0, 2)
    assert repo.get_room_by_id(db, room.id).number == "101"
    assert repo.get_room_by_id(db, 9999) is None

def test_create_user_duplicate(db):
    """Дублікат email викидає ValueError."""
    repo.create_user(db, "Test", "test@test.com")
    with pytest.raises(ValueError):
        repo.create_user(db, "Test2", "test@test.com")

def test_create_and_cancel_booking(db, hotel, user, future_dates):
    """Бронювання створюється зі статусом confirmed і скасовується."""
    room = repo.create_room(db, hotel.id, "101", "double", 1500.0, 2)
    check_in, check_out = future_dates
    booking = repo.create_booking(db, user.id, room.id, check_in, check_out, 3000.0)
    assert booking.status == "confirmed"
    cancelled = repo.cancel_booking(db, booking.id)
    assert cancelled.status == "cancelled"
    assert repo.cancel_booking(db, 9999) is None  # неіснуюче бронювання → None


# ── API ───────────────────────────────────────────────────────────────────────
# Інтеграційні тести REST API через TestClient + SQLite

def test_get_hotels_empty(client):
    """GET /hotels/ повертає порожній список якщо готелів немає."""
    assert client.get("/hotels/").status_code == 200

def test_create_and_get_hotel_api(client):
    """POST /hotels/ створює готель, GET /hotels/{id} повертає його."""
    r = client.post("/hotels/", json={"name": "Test", "city": "Київ", "address": "вул. 1", "stars": 4})
    assert r.status_code == 201
    assert client.get(f"/hotels/{r.json()['id']}").status_code == 200
    assert client.get("/hotels/9999").status_code == 404  # неіснуючий → 404

def test_create_hotel_invalid_stars(client):
    """POST /hotels/ з зірками > 5 повертає 422 (помилка валідації)."""
    r = client.post("/hotels/", json={"name": "H", "city": "Київ", "address": "вул. 1", "stars": 6})
    assert r.status_code == 422

def test_create_user_and_duplicate(client):
    """POST /users/ створює користувача, повторний email → 409."""
    r = client.post("/users/", json={"name": "Test", "email": "t@t.com"})
    assert r.status_code == 201
    r2 = client.post("/users/", json={"name": "Test2", "email": "t@t.com"})
    assert r2.status_code == 409  # дублікат email → конфлікт

def test_create_booking_and_cancel(client):
    """Повний сценарій: створити готель → кімнату → бронювання → скасувати."""
    # Створюємо готель і кімнату
    hotel_r = client.post("/hotels/", json={"name": "Hotel", "city": "Київ", "address": "вул. 1", "stars": 4})
    assert hotel_r.status_code == 201, f"Hotel creation failed: {hotel_r.text}"
    hotel = hotel_r.json()
    room_r = client.post(f"/hotels/{hotel['id']}/rooms/", json={
        "number": "101", "room_type": "double", "price_per_night": 1000, "capacity": 2
    })
    assert room_r.status_code == 201, f"Room creation failed: {room_r.text}"
    room = room_r.json()
    user_r = client.post("/users/", json={"name": "User", "email": "u@u.com"})
    assert user_r.status_code == 201, f"User creation failed: {user_r.text}"
    user = user_r.json()

    # Бронюємо кімнату
    today = date.today()
    booking = client.post("/bookings/", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": str(today + timedelta(1)), "check_out": str(today + timedelta(4))
    }).json()
    assert booking["status"] == "confirmed"

    # Скасовуємо — перший раз успішно, другий раз → 400
    assert client.post(f"/bookings/{booking['id']}/cancel").status_code == 200
    assert client.post(f"/bookings/{booking['id']}/cancel").status_code == 400
