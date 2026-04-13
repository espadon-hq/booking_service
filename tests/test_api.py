"""Тести для REST API ендпоінтів."""
from datetime import date, timedelta
import pytest


@pytest.fixture
def hotel(client):
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
    response = client.post(f"/hotels/{hotel['id']}/rooms/", json={
        "number": "101",
        "room_type": "double",
        "price_per_night": 1500.0,
        "capacity": 2,
    })
    return response.json()


@pytest.fixture
def user(client):
    response = client.post("/users/", json={
        "name": "Тест Користувач",
        "email": "test@example.com",
        "phone": "+380991234567",
    })
    return response.json()


@pytest.fixture
def future_dates():
    today = date.today()
    return {
        "check_in": str(today + timedelta(days=1)),
        "check_out": str(today + timedelta(days=4)),
    }


class TestHotelsAPI:
    def test_get_hotels_empty(self, client):
        response = client.get("/hotels/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_hotel(self, client):
        response = client.post("/hotels/", json={
            "name": "Grand Hotel",
            "city": "Київ",
            "address": "вул. Хрещатик, 1",
            "stars": 5,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Grand Hotel"
        assert "id" in data

    def test_get_hotel_by_id(self, client, hotel):
        response = client.get(f"/hotels/{hotel['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == hotel["id"]

    def test_get_hotel_not_found(self, client):
        response = client.get("/hotels/9999")
        assert response.status_code == 404

    def test_get_hotels_filter_by_city(self, client, hotel):
        response = client.get("/hotels/?city=Київ")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_update_hotel(self, client, hotel):
        response = client.patch(f"/hotels/{hotel['id']}", json={"name": "Updated Hotel", "stars": 5})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Hotel"

    def test_delete_hotel(self, client, hotel):
        response = client.delete(f"/hotels/{hotel['id']}")
        assert response.status_code == 200
        assert client.get(f"/hotels/{hotel['id']}").status_code == 404

    def test_create_hotel_invalid_stars(self, client):
        response = client.post("/hotels/", json={"name": "Hotel", "city": "Київ", "address": "вул. 1", "stars": 6})
        assert response.status_code == 422


class TestRoomsAPI:
    def test_get_rooms_empty(self, client, hotel):
        response = client.get(f"/hotels/{hotel['id']}/rooms/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_room(self, client, hotel):
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
        response = client.get(f"/hotels/{hotel['id']}/rooms/{room['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == room["id"]

    def test_get_available_rooms(self, client, hotel, room, future_dates):
        response = client.get(f"/hotels/{hotel['id']}/rooms/available", params=future_dates)
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) >= 1
        assert rooms[0]["available"] is True

    def test_delete_room(self, client, hotel, room):
        response = client.delete(f"/hotels/{hotel['id']}/rooms/{room['id']}")
        assert response.status_code == 200


class TestUsersAPI:
    def test_create_user(self, client):
        response = client.post("/users/", json={"name": "Іван Петренко", "email": "ivan@test.com"})
        assert response.status_code == 201
        assert response.json()["email"] == "ivan@test.com"

    def test_create_user_duplicate_email(self, client, user):
        response = client.post("/users/", json={"name": "Інший", "email": user["email"]})
        assert response.status_code == 409

    def test_get_user_by_id(self, client, user):
        response = client.get(f"/users/{user['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == user["id"]

    def test_get_user_not_found(self, client):
        response = client.get("/users/9999")
        assert response.status_code == 404

    def test_get_user_bookings_empty(self, client, user):
        response = client.get(f"/users/{user['id']}/bookings")
        assert response.status_code == 200
        assert response.json() == []


class TestBookingsAPI:
    def test_create_booking(self, client, user, room, future_dates):
        response = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            "check_in": future_dates["check_in"],
            "check_out": future_dates["check_out"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["total_price"] > 0

    def test_create_booking_invalid_dates(self, client, user, room):
        today = date.today()
        response = client.post("/bookings/", json={
            "user_id": user["id"],
            "room_id": room["id"],
            "check_in": str(today + timedelta(days=3)),
            "check_out": str(today + timedelta(days=1)),
        })
        assert response.status_code in (400, 422)

    def test_create_booking_room_unavailable(self, client, user, room, future_dates):
        client.post("/bookings/", json={"user_id": user["id"], "room_id": room["id"], **future_dates})
        response = client.post("/bookings/", json={"user_id": user["id"], "room_id": room["id"], **future_dates})
        assert response.status_code == 400

    def test_get_booking_by_id(self, client, user, room, future_dates):
        created = client.post("/bookings/", json={"user_id": user["id"], "room_id": room["id"], **future_dates}).json()
        response = client.get(f"/bookings/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_cancel_booking(self, client, user, room, future_dates):
        created = client.post("/bookings/", json={"user_id": user["id"], "room_id": room["id"], **future_dates}).json()
        response = client.post(f"/bookings/{created['id']}/cancel")
        assert response.status_code == 200

    def test_cancel_already_cancelled(self, client, user, room, future_dates):
        created = client.post("/bookings/", json={"user_id": user["id"], "room_id": room["id"], **future_dates}).json()
        client.post(f"/bookings/{created['id']}/cancel")
        response = client.post(f"/bookings/{created['id']}/cancel")
        assert response.status_code == 400
