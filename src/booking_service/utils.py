"""Утиліти та бізнес-логіка системи бронювання.

Лаб 1 — чисті функції без залежностей від БД або API.
"""

from datetime import date

from booking_service.models import Booking, Hotel, Room


def calculate_total_price(room: Room, check_in: date, check_out: date) -> float:
    """Розраховує загальну вартість бронювання.

    Args:
        room: Об'єкт кімнати з ціною за ніч.
        check_in: Дата заїзду.
        check_out: Дата виїзду.

    Returns:
        Загальна вартість у гривнях.

    Raises:
        ValueError: Якщо дата виїзду не пізніше дати заїзду.
    """
    if check_out <= check_in:
        raise ValueError("Дата виїзду повинна бути пізніше дати заїзду.")

    nights = (check_out - check_in).days
    return round(room.price_per_night * nights, 2)


def is_dates_valid(check_in: date, check_out: date) -> bool:
    """Перевіряє чи дати бронювання коректні.

    Умови:
        - Дата заїзду не в минулому.
        - Дата виїзду пізніше дати заїзду.

    Args:
        check_in: Дата заїзду.
        check_out: Дата виїзду.

    Returns:
        True якщо дати коректні, False інакше.
    """
    today = date.today()

    # Заїзд не може бути в минулому
    if check_in < today:
        return False

    # Виїзд повинен бути пізніше заїзду
    if check_out <= check_in:
        return False

    return True


def is_room_available(
    room_id: int,
    check_in: date,
    check_out: date,
    existing_bookings: list[Booking],
) -> bool:
    """Перевіряє чи кімната вільна на вказані дати.

    Кімната зайнята якщо існує бронювання що перетинається
    з запитуваним періодом і має статус не 'cancelled'.

    Args:
        room_id: Ідентифікатор кімнати.
        check_in: Бажана дата заїзду.
        check_out: Бажана дата виїзду.
        existing_bookings: Список існуючих бронювань для перевірки.

    Returns:
        True якщо кімната вільна, False якщо зайнята.
    """
    for booking in existing_bookings:
        # Перевіряємо лише активні бронювання цієї кімнати
        if booking.room_id != room_id:
            continue
        if booking.status == "cancelled":
            continue

        # Перевіряємо перетин дат
        if check_in < booking.check_out and check_out > booking.check_in:
            return False

    return True


def filter_hotels_by_city(hotels: list[Hotel], city: str) -> list[Hotel]:
    """Фільтрує готелі за містом без урахування регістру.

    Args:
        hotels: Список готелів.
        city: Назва міста для фільтрації.

    Returns:
        Список готелів у вказаному місті.
    """
    return [h for h in hotels if h.city.lower() == city.lower()]


def filter_rooms_by_price(
    rooms: list[Room],
    max_price: float,
) -> list[Room]:
    """Фільтрує кімнати за максимальною ціною за ніч.

    Args:
        rooms: Список кімнат.
        max_price: Максимальна ціна за ніч у гривнях.

    Returns:
        Список кімнат що не перевищують вказану ціну.
    """
    return [r for r in rooms if r.price_per_night <= max_price]