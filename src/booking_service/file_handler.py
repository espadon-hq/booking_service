"""Модуль роботи з файлами — імпорт та експорт даних.

Лаб 3 — читання та запис CSV і JSON файлів.
Підтримує експорт готелів, кімнат, користувачів та бронювань.
"""

import csv
import json
import os
from datetime import date
from typing import Any

from booking_service.models import Booking, Hotel, Room, User

# ── Допоміжні функції ─────────────────────────────────────────────────────────


def _ensure_dir(filepath: str) -> None:
    """Створює директорію для файлу якщо вона не існує.

    Args:
        filepath: Повний шлях до файлу.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def _date_to_str(d: date) -> str:
    """Конвертує date в рядок формату РРРР-ММ-ДД.

    Args:
        d: Об'єкт дати.

    Returns:
        Рядкове представлення дати.
    """
    return d.isoformat()


def _str_to_date(s: str) -> date:
    """Конвертує рядок формату РРРР-ММ-ДД в date.

    Args:
        s: Рядок з датою.

    Returns:
        Об'єкт дати.

    Raises:
        ValueError: Якщо рядок не відповідає формату.
    """
    return date.fromisoformat(s)


# ── CSV ───────────────────────────────────────────────────────────────────────


def export_hotels_csv(hotels: list[Hotel], filepath: str) -> None:
    """Експортує список готелів у CSV файл.

    Args:
        hotels: Список готелів для експорту.
        filepath: Шлях до файлу збереження.
    """
    _ensure_dir(filepath)

    # Назви колонок — заголовок CSV файлу
    fieldnames = ["id", "name", "city", "address", "stars", "description"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for hotel in hotels:
            writer.writerow({
                "id": hotel.id,
                "name": hotel.name,
                "city": hotel.city,
                "address": hotel.address,
                "stars": hotel.stars,
                "description": hotel.description,
            })


def import_hotels_csv(filepath: str) -> list[Hotel]:
    """Імпортує список готелів з CSV файлу.

    Args:
        filepath: Шлях до CSV файлу.

    Returns:
        Список об'єктів Hotel.

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
        ValueError: Якщо файл має некоректну структуру.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не знайдено: {filepath}")

    hotels = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Перевіряємо наявність обов'язкових колонок
        required = {"id", "name", "city", "address", "stars"}
        if reader.fieldnames and not required.issubset(set(reader.fieldnames)):
            missing = required - set(reader.fieldnames)
            raise ValueError(f"Відсутні обов'язкові колонки: {missing}")

        for row in reader:
            # Пропускаємо порожні рядки
            if not row.get("name"):
                continue

            hotels.append(Hotel(
                id=int(row["id"]),
                name=row["name"],
                city=row["city"],
                address=row["address"],
                stars=int(row["stars"]),
                description=row.get("description", ""),
            ))

    return hotels


def export_rooms_csv(rooms: list[Room], filepath: str) -> None:
    """Експортує список кімнат у CSV файл.

    Args:
        rooms: Список кімнат для експорту.
        filepath: Шлях до файлу збереження.
    """
    _ensure_dir(filepath)

    fieldnames = ["id", "hotel_id", "number", "room_type",
                  "price_per_night", "capacity"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for room in rooms:
            writer.writerow({
                "id": room.id,
                "hotel_id": room.hotel_id,
                "number": room.number,
                "room_type": room.room_type,
                "price_per_night": room.price_per_night,
                "capacity": room.capacity,
            })


def import_rooms_csv(filepath: str) -> list[Room]:
    """Імпортує список кімнат з CSV файлу.

    Args:
        filepath: Шлях до CSV файлу.

    Returns:
        Список об'єктів Room.

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
        ValueError: Якщо файл має некоректну структуру.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не знайдено: {filepath}")

    rooms = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {"id", "hotel_id", "number", "room_type", "price_per_night"}
        if reader.fieldnames and not required.issubset(set(reader.fieldnames)):
            missing = required - set(reader.fieldnames)
            raise ValueError(f"Відсутні обов'язкові колонки: {missing}")

        for row in reader:
            if not row.get("number"):
                continue

            rooms.append(Room(
                id=int(row["id"]),
                hotel_id=int(row["hotel_id"]),
                number=row["number"],
                room_type=row["room_type"],
                price_per_night=float(row["price_per_night"]),
                capacity=int(row.get("capacity", 2)),
            ))

    return rooms


def export_bookings_csv(bookings: list[Booking], filepath: str) -> None:
    """Експортує список бронювань у CSV файл.

    Args:
        bookings: Список бронювань для експорту.
        filepath: Шлях до файлу збереження.
    """
    _ensure_dir(filepath)

    fieldnames = ["id", "user_id", "room_id", "check_in",
                  "check_out", "total_price", "status"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for b in bookings:
            writer.writerow({
                "id": b.id,
                "user_id": b.user_id,
                "room_id": b.room_id,
                "check_in": _date_to_str(b.check_in),
                "check_out": _date_to_str(b.check_out),
                "total_price": b.total_price,
                "status": b.status,
            })


def import_bookings_csv(filepath: str) -> list[Booking]:
    """Імпортує список бронювань з CSV файлу.

    Args:
        filepath: Шлях до CSV файлу.

    Returns:
        Список об'єктів Booking.

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
        ValueError: Якщо файл має некоректну структуру.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не знайдено: {filepath}")

    bookings = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {"id", "user_id", "room_id", "check_in",
                    "check_out", "total_price"}
        if reader.fieldnames and not required.issubset(set(reader.fieldnames)):
            missing = required - set(reader.fieldnames)
            raise ValueError(f"Відсутні обов'язкові колонки: {missing}")

        for row in reader:
            bookings.append(Booking(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                room_id=int(row["room_id"]),
                check_in=_str_to_date(row["check_in"]),
                check_out=_str_to_date(row["check_out"]),
                total_price=float(row["total_price"]),
                status=row.get("status", "pending"),
            ))

    return bookings


# ── JSON ──────────────────────────────────────────────────────────────────────


def _hotel_to_dict(hotel: Hotel) -> dict[str, Any]:
    """Конвертує Hotel в словник для серіалізації в JSON."""
    return {
        "id": hotel.id,
        "name": hotel.name,
        "city": hotel.city,
        "address": hotel.address,
        "stars": hotel.stars,
        "description": hotel.description,
    }


def _room_to_dict(room: Room) -> dict[str, Any]:
    """Конвертує Room в словник для серіалізації в JSON."""
    return {
        "id": room.id,
        "hotel_id": room.hotel_id,
        "number": room.number,
        "room_type": room.room_type,
        "price_per_night": room.price_per_night,
        "capacity": room.capacity,
    }


def _booking_to_dict(booking: Booking) -> dict[str, Any]:
    """Конвертує Booking в словник для серіалізації в JSON."""
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "check_in": _date_to_str(booking.check_in),
        "check_out": _date_to_str(booking.check_out),
        "total_price": booking.total_price,
        "status": booking.status,
    }


def _user_to_dict(user: User) -> dict[str, Any]:
    """Конвертує User в словник для серіалізації в JSON."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
    }


def export_json(
    hotels: list[Hotel],
    rooms: list[Room],
    bookings: list[Booking],
    users: list[User],
    filepath: str,
) -> None:
    """Експортує всі дані системи в один JSON файл.

    Args:
        hotels: Список готелів.
        rooms: Список кімнат.
        bookings: Список бронювань.
        users: Список користувачів.
        filepath: Шлях до файлу збереження.
    """
    _ensure_dir(filepath)

    # Збираємо всі дані в один словник
    data = {
        "hotels": [_hotel_to_dict(h) for h in hotels],
        "rooms": [_room_to_dict(r) for r in rooms],
        "bookings": [_booking_to_dict(b) for b in bookings],
        "users": [_user_to_dict(u) for u in users],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        # indent=2 — зручне форматування для читання людиною
        # ensure_ascii=False — зберігаємо кирилицю без екранування
        json.dump(data, f, indent=2, ensure_ascii=False)


def import_json(filepath: str) -> dict[str, list]:
    """Імпортує всі дані системи з JSON файлу.

    Args:
        filepath: Шлях до JSON файлу.

    Returns:
        Словник з ключами 'hotels', 'rooms', 'bookings', 'users' —
        кожен містить список відповідних об'єктів.

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
        ValueError: Якщо структура JSON некоректна.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не знайдено: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    # Перевіряємо наявність обов'язкових секцій
    required_keys = {"hotels", "rooms", "bookings", "users"}
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"Відсутні обов'язкові секції в JSON: {missing}")

    # Конвертуємо словники назад в об'єкти
    hotels = [
        Hotel(
            id=h["id"],
            name=h["name"],
            city=h["city"],
            address=h["address"],
            stars=h["stars"],
            description=h.get("description", ""),
        )
        for h in data["hotels"]
    ]

    rooms = [
        Room(
            id=r["id"],
            hotel_id=r["hotel_id"],
            number=r["number"],
            room_type=r["room_type"],
            price_per_night=r["price_per_night"],
            capacity=r.get("capacity", 2),
        )
        for r in data["rooms"]
    ]

    bookings = [
        Booking(
            id=b["id"],
            user_id=b["user_id"],
            room_id=b["room_id"],
            check_in=_str_to_date(b["check_in"]),
            check_out=_str_to_date(b["check_out"]),
            total_price=b["total_price"],
            status=b.get("status", "pending"),
        )
        for b in data["bookings"]
    ]

    users = [
        User(
            id=u["id"],
            name=u["name"],
            email=u["email"],
            phone=u.get("phone", ""),
        )
        for u in data["users"]
    ]

    return {
        "hotels": hotels,
        "rooms": rooms,
        "bookings": bookings,
        "users": users,
    }