"""Тести для REST API ендпоінтів.

Використовує SQLite in-memory та TestClient від FastAPI.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from booking_service.database import Base, get_db
from booking_service.main import app

# ── Налаштування тестової БД ──────────────────────────────────────────────────


@pytest.fixture(scope="function")
def client():
    """Створює тестовий клієнт з ізольованою SQLite БД."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        """Замінює продуктивну БД на тестову."""
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    # Замінюємо залежність get_db на тестову
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Прибираємо override після тесту
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def hotel(client):
    """Створює тестовий готель через API."""
    response = client.post("/hotels/", json={
        "name": "Test Hotel",
        "city": "Київ",
        "address": "вул. Тестова, 1",
        "stars": 4,
        "description": "Тестовий готель",
    })
    return response.json()


@pytest.fixture
def room(client, hotel):
    """Створює тестову кімнату через API."""
    response = client.post(f"/hotels/{hotel['id']}/rooms/", json={
        "number": "101",
        "room_type": "double",
        "price_per_night": 1500.0,
        "capacity": 2,
    })
    return response.json()


@pytest.fixture
def user(client):
    """Створює тестового користувача через API."""
    response = client.post("/users/", json={
        "name": "Тест Користувач",
        "email": "test@example.com",
        "phone": "+380991234567",
    })
    return response.json()


@pytest.fixture
def future_dates():
    """Повертає майбутні дати."""
    today = date.today()
    return {
        "check_in": str(today + timedelta(days=1)),
        "check_out": str(today + timedelta(days=4)),
    }


# ── Hotels ────────────────────────────────────────────────────────────────────


class TestHotelsAPI:
    """Тести для /hotels ендпоінтів."""

    def test_get_hotels_empty(self, client):
        """GET /hotels/ повертає порожній список."""
        response = client.get("/hotels/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_hotel(self, client):
        """POST /hotels/ створює готель."""
        response = client.post("/hotels/", json={
            "name": "Grand Hotel",
            "city": "Київ",
            "address": "вул. Хрещатик, 1",
            "stars": 5,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Grand Hotel"
        assert data["stars"] == 5
        assert "id" in data

    def test_get_hotel_by_id(self, client, hotel):
        """GET /hotels/{id} повертає готель."""
        response = client.get(f"/hotels/{hotel['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == hotel["id"]

    def test_get_hotel_not_found(self, client):
        """GET /hotels/{id} повертає 404 для неіснуючого."""
        response = client.get("/hotels/9999")
        assert response.status_code == 404

    def test_get_hotels_filter_by_city(self, client, hotel):
        """GET /hotels/?city= фільтрує за містом."""
        response = client.get("/hotels/?city=Київ")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_update_hotel(self, client, hotel):
        """PATCH /hotels/{id} оновлює поля."""
        response = client.patch(f"/hotels/{hotel['id']}", json={
            "name": "Updated Hotel",
            "stars": 5,
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Hotel"

    def test_delete_hotel(self, client, hotel):
        """DELETE /hotels/{id} видаляє готель."""
        response = client.delete(f"/hotels/{hotel['id']}")
        assert response.status_code == 200
        assert client.get(f"/hotels/{hotel['id']}").status_code == 404

    def test_create_hotel_invalid_stars(self, client):
        """POST /hotels/ з зірками > 5 повертає 422."""
        response = client.post("/hotels/", json={
            "name": "Hotel",
            "city": "Київ",
            "address": "вул. 1",
            "stars": 6,
        })
        assert response.status_code == 422


# ── Rooms ─────────────────────────────────────────────────────────────────────


class TestRoomsAPI:
    """Тести для /hotels/{id}/rooms ендпоінтів."""

    def test_get_rooms_empty(self, client, hotel):
        """GET /hotels/{id}/rooms/ повертає порожній список."""
        response = client.get(f"/hotels/{hotel['id']}/rooms/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_room(self, client, hotel):
        """POST /hotels/{id}/rooms/ створює кімнату."""
        response = client.post(f"/hotels/{hotel['id']}/rooms/", json={
            "number": "202",
            "room_type": "suite",
            "price_per_night": 3000.0,
            "capacity": 3,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["number"] == "202"
        assert data["hotel_id"] == hotel["id"]

    def test_get_room_by_id(self, client, hotel, room):
        """GET /hotels/{id}/rooms/{room_id} повертає кімнату."""
        response = client.get(f"/hotels/{hotel['id']}/rooms/{room['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == room["id"]

    def test_get_available_rooms(self, client, hotel, room, future_dates):
        """GET /hotels/{id}/rooms/available повертає вільні кімнати."""
        response = client.get(
            f"/hotels/{hotel['id']}/rooms/available",
            params=future_dates,
        )
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) >= 1
        assert rooms[0]["available"] is True
        assert rooms[0]["total_price"] is not None

    def test_delete_room(self, client, hotel, room):
        """DELETE /hotels/{id}/rooms/{room_id} видаляє кімнату."""
        response = client.delete(f"/hotels/{hotel['id']}/rooms/{room['id']}")
        assert response.status_code == 200


# ── Users ─────────────────────────────────────────────────────────────────────


class TestUsersAPI:
    """Тести для /users ендпоінтів."""

    def test_create_user(self, client):
        """POST /users/ створює користувача."""
        response = client.post("/users/", json={
            "name": "Іван Петренко",
            "email": "ivan@test.com",
        })
        assert response.status_code == 201
        assert response.json()["email"] == "ivan@test.com"

    def test_create_user_duplicate_email(self, client, user):
        """POST /users/ з дублікатом email повертає 409."""
        response = client.post("/users/", json={
            "name": "Інший",
            "email": user["email"],
        })
        assert response.status_code == 409

    def test_get_user_by_id(self, client, user):
        """GET /users/{id} повертає користувача."""
        response = client.get(f"/users/{user['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == user["id"]

    def test_get_user_not_found(self, client):
        """GET /users/{id} повертає 404."""
        response = client.get("/users/9999")
        assert response.status_code == 404

    def test_get_user_bookings_empty(self, client, user):
        """GET /users/{id}/bookings повертає порожній список."""
        response = client.get(f"/users/{user['id']}/bookings")
        assert response.status_code == 200
        assert response.json() == []


# ── Bookings ──────────────────────────────────────────────────────────────────


class TestBookingsAPI:
    """Тести для /bookings ендпоінтів."""

    def test_create_booking(self, client, user, room, future_dates):
        """POST /bookings/ створює бронювання."""
        response = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            "check_in": future_dates["check_in"],
            "check_out": future_dates["check_out"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["user_id"] == user["id"]
        assert data["room_id"] == room["id"]
        assert data["total_price"] > 0

    def test_create_booking_invalid_dates(self, client, user, room):
        """POST /bookings/ з некоректними датами повертає 400 або 422."""
        today = date.today()
        response = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            "check_in": str(today + timedelta(days=3)),
            "check_out": str(today + timedelta(days=1)),
        })
        assert response.status_code in (400, 422)

    def test_create_booking_room_unavailable(
        self, client, user, room, future_dates
    ):
        """POST /bookings/ на зайняту кімнату повертає 400."""
        # Перше бронювання
        client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            **future_dates,
        })
        # Друге бронювання на ті самі дати
        response = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            **future_dates,
        })
        assert response.status_code == 400

    def test_get_booking_by_id(self, client, user, room, future_dates):
        """GET /bookings/{id} повертає бронювання."""
        created = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            **future_dates,
        }).json()
        response = client.get(f"/bookings/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_cancel_booking(self, client, user, room, future_dates):
        """POST /bookings/{id}/cancel скасовує бронювання."""
        created = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            **future_dates,
        }).json()
        response = client.post(f"/bookings/{created['id']}/cancel")
        assert response.status_code == 200

    def test_cancel_already_cancelled(self, client, user, room, future_dates):
        """POST /bookings/{id}/cancel повторно повертає 400."""
        created = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            **future_dates,
        }).json()
        client.post(f"/bookings/{created['id']}/cancel")
        response = client.post(f"/bookings/{created['id']}/cancel")
        assert response.status_code == 400