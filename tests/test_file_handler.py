"""Тести для модуля роботи з файлами — file_handler.py."""

import os
from datetime import date, timedelta

import pytest

from booking_service.file_handler import (
    export_bookings_csv,
    export_hotels_csv,
    export_json,
    export_rooms_csv,
    import_bookings_csv,
    import_hotels_csv,
    import_json,
    import_rooms_csv,
)
from booking_service.models import Booking, Hotel, Room, User

# ── Фікстури ──────────────────────────────────────────────────────────────────


@pytest.fixture
def hotels() -> list[Hotel]:
    """Список тестових готелів."""
    return [
        Hotel(1, "Grand Hotel", "Київ", "вул. Хрещатик, 1", 5, "Опис 1"),
        Hotel(2, "City Inn", "Одеса", "вул. Морська, 5", 3, "Опис 2"),
    ]


@pytest.fixture
def rooms() -> list[Room]:
    """Список тестових кімнат."""
    return [
        Room(1, 1, "101", "single", 1500.0, 1),
        Room(2, 1, "202", "double", 2500.0, 2),
    ]


@pytest.fixture
def users() -> list[User]:
    """Список тестових користувачів."""
    return [
        User(1, "Іван Петренко", "ivan@example.com", "+380991234567"),
        User(2, "Марія Коваль", "maria@example.com", ""),
    ]


@pytest.fixture
def bookings() -> list[Booking]:
    """Список тестових бронювань."""
    today = date.today()
    return [
        Booking(
            id=1,
            user_id=1,
            room_id=1,
            check_in=today + timedelta(days=1),
            check_out=today + timedelta(days=4),
            total_price=4500.0,
            status="confirmed",
        ),
        Booking(
            id=2,
            user_id=2,
            room_id=2,
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=7),
            total_price=5000.0,
            status="pending",
        ),
    ]


# ── CSV — Готелі ──────────────────────────────────────────────────────────────


class TestExportImportHotelsCsv:
    """Тести для export_hotels_csv() та import_hotels_csv()."""

    def test_export_creates_file(self, hotels, tmp_path):
        """Експорт створює CSV файл."""
        filepath = str(tmp_path / "hotels.csv")
        export_hotels_csv(hotels, filepath)
        assert os.path.exists(filepath)

    def test_export_import_roundtrip(self, hotels, tmp_path):
        """Імпорт після експорту повертає ті самі дані."""
        filepath = str(tmp_path / "hotels.csv")
        export_hotels_csv(hotels, filepath)
        imported = import_hotels_csv(filepath)

        assert len(imported) == len(hotels)
        assert imported[0].name == hotels[0].name
        assert imported[0].city == hotels[0].city
        assert imported[0].stars == hotels[0].stars
        assert imported[1].name == hotels[1].name

    def test_export_empty_list(self, tmp_path):
        """Експорт порожнього списку створює файл лише з заголовком."""
        filepath = str(tmp_path / "empty.csv")
        export_hotels_csv([], filepath)
        imported = import_hotels_csv(filepath)
        assert imported == []

    def test_import_nonexistent_file(self):
        """Імпорт неіснуючого файлу викидає FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            import_hotels_csv("/nonexistent/path/hotels.csv")

    def test_import_preserves_description(self, hotels, tmp_path):
        """Імпорт зберігає опис готелю."""
        filepath = str(tmp_path / "hotels.csv")
        export_hotels_csv(hotels, filepath)
        imported = import_hotels_csv(filepath)
        assert imported[0].description == hotels[0].description

    def test_import_preserves_id(self, hotels, tmp_path):
        """Імпорт зберігає id готелю."""
        filepath = str(tmp_path / "hotels.csv")
        export_hotels_csv(hotels, filepath)
        imported = import_hotels_csv(filepath)
        assert imported[0].id == hotels[0].id
        assert imported[1].id == hotels[1].id


# ── CSV — Кімнати ─────────────────────────────────────────────────────────────


class TestExportImportRoomsCsv:
    """Тести для export_rooms_csv() та import_rooms_csv()."""

    def test_export_creates_file(self, rooms, tmp_path):
        """Експорт створює CSV файл."""
        filepath = str(tmp_path / "rooms.csv")
        export_rooms_csv(rooms, filepath)
        assert os.path.exists(filepath)

    def test_export_import_roundtrip(self, rooms, tmp_path):
        """Імпорт після експорту повертає ті самі дані."""
        filepath = str(tmp_path / "rooms.csv")
        export_rooms_csv(rooms, filepath)
        imported = import_rooms_csv(filepath)

        assert len(imported) == len(rooms)
        assert imported[0].number == rooms[0].number
        assert imported[0].price_per_night == rooms[0].price_per_night
        assert imported[0].capacity == rooms[0].capacity

    def test_import_nonexistent_file(self):
        """Імпорт неіснуючого файлу викидає FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            import_rooms_csv("/nonexistent/path/rooms.csv")

    def test_preserves_hotel_id(self, rooms, tmp_path):
        """Імпорт зберігає hotel_id кімнати."""
        filepath = str(tmp_path / "rooms.csv")
        export_rooms_csv(rooms, filepath)
        imported = import_rooms_csv(filepath)
        assert imported[0].hotel_id == rooms[0].hotel_id


# ── CSV — Бронювання ──────────────────────────────────────────────────────────


class TestExportImportBookingsCsv:
    """Тести для export_bookings_csv() та import_bookings_csv()."""

    def test_export_creates_file(self, bookings, tmp_path):
        """Експорт створює CSV файл."""
        filepath = str(tmp_path / "bookings.csv")
        export_bookings_csv(bookings, filepath)
        assert os.path.exists(filepath)

    def test_export_import_roundtrip(self, bookings, tmp_path):
        """Імпорт після експорту повертає ті самі дані."""
        filepath = str(tmp_path / "bookings.csv")
        export_bookings_csv(bookings, filepath)
        imported = import_bookings_csv(filepath)

        assert len(imported) == len(bookings)
        assert imported[0].check_in == bookings[0].check_in
        assert imported[0].check_out == bookings[0].check_out
        assert imported[0].total_price == bookings[0].total_price
        assert imported[0].status == bookings[0].status

    def test_dates_preserved_correctly(self, bookings, tmp_path):
        """Дати зберігаються та відновлюються коректно."""
        filepath = str(tmp_path / "bookings.csv")
        export_bookings_csv(bookings, filepath)
        imported = import_bookings_csv(filepath)
        assert isinstance(imported[0].check_in, date)
        assert isinstance(imported[0].check_out, date)

    def test_import_nonexistent_file(self):
        """Імпорт неіснуючого файлу викидає FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            import_bookings_csv("/nonexistent/path/bookings.csv")


# ── JSON ──────────────────────────────────────────────────────────────────────


class TestExportImportJson:
    """Тести для export_json() та import_json()."""

    def test_export_creates_file(self, hotels, rooms, bookings, users, tmp_path):
        """Експорт створює JSON файл."""
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)
        assert os.path.exists(filepath)

    def test_export_import_roundtrip(self, hotels, rooms, bookings, users, tmp_path):
        """Імпорт після експорту повертає ті самі дані."""
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)
        data = import_json(filepath)

        assert len(data["hotels"]) == len(hotels)
        assert len(data["rooms"]) == len(rooms)
        assert len(data["bookings"]) == len(bookings)
        assert len(data["users"]) == len(users)

    def test_hotels_data_preserved(self, hotels, rooms, bookings, users, tmp_path):
        """Дані готелів зберігаються коректно."""
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)
        data = import_json(filepath)

        assert data["hotels"][0].name == hotels[0].name
        assert data["hotels"][0].city == hotels[0].city
        assert data["hotels"][0].stars == hotels[0].stars

    def test_bookings_dates_preserved(self, hotels, rooms, bookings, users, tmp_path):
        """Дати бронювань зберігаються коректно."""
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)
        data = import_json(filepath)

        assert data["bookings"][0].check_in == bookings[0].check_in
        assert data["bookings"][0].check_out == bookings[0].check_out

    def test_users_data_preserved(self, hotels, rooms, bookings, users, tmp_path):
        """Дані користувачів зберігаються коректно."""
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)
        data = import_json(filepath)

        assert data["users"][0].name == users[0].name
        assert data["users"][0].email == users[0].email

    def test_import_nonexistent_file(self):
        """Імпорт неіснуючого файлу викидає FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            import_json("/nonexistent/path/data.json")

    def test_file_is_valid_json(self, hotels, rooms, bookings, users, tmp_path):
        """Експортований файл є валідним JSON."""
        import json
        filepath = str(tmp_path / "data.json")
        export_json(hotels, rooms, bookings, users, filepath)

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        assert "hotels" in data
        assert "rooms" in data
        assert "bookings" in data
        assert "users" in data

    def test_export_empty_data(self, tmp_path):
        """Експорт порожніх списків створює валідний JSON."""
        filepath = str(tmp_path / "empty.json")
        export_json([], [], [], [], filepath)
        data = import_json(filepath)

        assert data["hotels"] == []
        assert data["rooms"] == []
        assert data["bookings"] == []
        assert data["users"] == []