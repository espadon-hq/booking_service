"""Прості дата-класи для основних сутностей системи.

"""

from dataclasses import dataclass
from datetime import date


@dataclass
class Hotel:
    """Готель.

    Attributes:
        id: Унікальний ідентифікатор.
        name: Назва готелю.
        city: Місто розташування.
        address: Повна адреса.
        stars: Кількість зірок (1-5).
        description: Опис готелю.
    """

    id: int
    name: str
    city: str
    address: str
    stars: int
    description: str = ""

    def __str__(self) -> str:
        """Рядкове представлення готелю."""
        return f"[{self.stars}*] {self.name} — {self.city}"


@dataclass
class Room:
    """Кімната в готелі.

    Attributes:
        id: Унікальний ідентифікатор.
        hotel_id: Ідентифікатор готелю якому належить кімната.
        number: Номер кімнати (наприклад '101', '202A').
        room_type: Тип кімнати — single, double, suite.
        price_per_night: Ціна за одну ніч у гривнях.
        capacity: Максимальна кількість гостей.
    """

    id: int
    hotel_id: int
    number: str
    room_type: str
    price_per_night: float
    capacity: int = 2

    def __str__(self) -> str:
        """Рядкове представлення кімнати."""
        return (
            f"Кімната {self.number} ({self.room_type})"
            f" — {self.price_per_night} грн/ніч"
        )


@dataclass
class User:
    """Користувач системи.

    Attributes:
        id: Унікальний ідентифікатор.
        name: Повне ім'я.
        email: Електронна пошта.
        phone: Номер телефону.
    """

    id: int
    name: str
    email: str
    phone: str = ""

    def __str__(self) -> str:
        """Рядкове представлення користувача."""
        return f"{self.name} <{self.email}>"


@dataclass
class Booking:
    """Бронювання кімнати.

    Attributes:
        id: Унікальний ідентифікатор.
        user_id: Ідентифікатор користувача.
        room_id: Ідентифікатор кімнати.
        check_in: Дата заїзду.
        check_out: Дата виїзду.
        total_price: Загальна вартість бронювання.
        status: Статус — pending, confirmed, cancelled.
    """

    id: int
    user_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: float
    status: str = "pending"

    def nights(self) -> int:
        """Повертає кількість ночей бронювання.

        Returns:
            Кількість ночей як ціле число.
        """
        return (self.check_out - self.check_in).days

    def __str__(self) -> str:
        """Рядкове представлення бронювання."""
        return (
            f"Бронювання #{self.id} | "
            f"{self.check_in} — {self.check_out} "
            f"({self.nights()} ночей) | "
            f"{self.total_price} грн | {self.status}"
        )