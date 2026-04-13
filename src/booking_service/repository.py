"""Репозиторій — функції для роботи з БД.

Лаб 4 — всі операції з базою даних зосереджені тут.
Роутери та консоль не взаємодіють з БД напряму —
лише через функції цього модуля.
"""

from datetime import date

from sqlalchemy.orm import Session

from booking_service.db_models import Booking, Hotel, Room, User
from booking_service.utils import is_room_available as check_available

# ── Hotel ─────────────────────────────────────────────────────────────────────


def get_all_hotels(db: Session) -> list[Hotel]:
    """Повертає всі готелі відсортовані за назвою.

    Args:
        db: Активна сесія БД.

    Returns:
        Список всіх готелів.
    """
    return db.query(Hotel).order_by(Hotel.name).all()


def get_hotel_by_id(db: Session, hotel_id: int) -> Hotel | None:
    """Повертає готель за id або None.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.

    Returns:
        Об'єкт Hotel або None якщо не знайдено.
    """
    return db.query(Hotel).filter(Hotel.id == hotel_id).first()


def get_hotels_by_city(db: Session, city: str) -> list[Hotel]:
    """Повертає готелі у вказаному місті (без урахування регістру).

    Args:
        db: Активна сесія БД.
        city: Назва міста.

    Returns:
        Список готелів у місті.
    """
    all_hotels = db.query(Hotel).order_by(Hotel.stars.desc()).all()
    return [h for h in all_hotels if h.city.lower() == city.lower()]


def create_hotel(
    db: Session,
    name: str,
    city: str,
    address: str,
    stars: int,
    description: str = "",
) -> Hotel:
    """Створює новий готель та зберігає в БД.

    Args:
        db: Активна сесія БД.
        name: Назва готелю.
        city: Місто.
        address: Адреса.
        stars: Кількість зірок (1-5).
        description: Опис готелю.

    Returns:
        Створений об'єкт Hotel з id з БД.
    """
    hotel = Hotel(
        name=name,
        city=city,
        address=address,
        stars=stars,
        description=description,
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


def update_hotel(
    db: Session,
    hotel_id: int,
    **kwargs,
) -> Hotel | None:
    """Оновлює поля готелю.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.
        **kwargs: Поля для оновлення (name, city, address, stars, description).

    Returns:
        Оновлений об'єкт Hotel або None якщо не знайдено.
    """
    hotel = get_hotel_by_id(db, hotel_id)
    if not hotel:
        return None

    # Оновлюємо лише передані поля
    for key, value in kwargs.items():
        if hasattr(hotel, key):
            setattr(hotel, key, value)

    db.commit()
    db.refresh(hotel)
    return hotel


def delete_hotel(db: Session, hotel_id: int) -> bool:
    """Видаляє готель з БД разом з кімнатами та бронюваннями.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.

    Returns:
        True якщо видалено, False якщо не знайдено.
    """
    hotel = get_hotel_by_id(db, hotel_id)
    if not hotel:
        return False

    db.delete(hotel)
    db.commit()
    return True


# ── Room ──────────────────────────────────────────────────────────────────────


def get_rooms_by_hotel(db: Session, hotel_id: int) -> list[Room]:
    """Повертає всі кімнати готелю.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.

    Returns:
        Список кімнат готелю.
    """
    return (
        db.query(Room)
        .filter(Room.hotel_id == hotel_id)
        .order_by(Room.number)
        .all()
    )


def get_room_by_id(db: Session, room_id: int) -> Room | None:
    """Повертає кімнату за id або None.

    Args:
        db: Активна сесія БД.
        room_id: Ідентифікатор кімнати.

    Returns:
        Об'єкт Room або None.
    """
    return db.query(Room).filter(Room.id == room_id).first()


def create_room(
    db: Session,
    hotel_id: int,
    number: str,
    room_type: str,
    price_per_night: float,
    capacity: int = 2,
) -> Room:
    """Створює нову кімнату в готелі.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.
        number: Номер кімнати.
        room_type: Тип кімнати.
        price_per_night: Ціна за ніч.
        capacity: Місткість.

    Returns:
        Створений об'єкт Room з id з БД.
    """
    room = Room(
        hotel_id=hotel_id,
        number=number,
        room_type=room_type,
        price_per_night=price_per_night,
        capacity=capacity,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room_id: int) -> bool:
    """Видаляє кімнату з БД.

    Args:
        db: Активна сесія БД.
        room_id: Ідентифікатор кімнати.

    Returns:
        True якщо видалено, False якщо не знайдено.
    """
    room = get_room_by_id(db, room_id)
    if not room:
        return False
    db.delete(room)
    db.commit()
    return True


def get_available_rooms(
    db: Session,
    hotel_id: int,
    check_in: date,
    check_out: date,
) -> list[Room]:
    """Повертає вільні кімнати готелю на вказані дати.

    Args:
        db: Активна сесія БД.
        hotel_id: Ідентифікатор готелю.
        check_in: Дата заїзду.
        check_out: Дата виїзду.

    Returns:
        Список вільних кімнат.
    """
    # Отримуємо всі кімнати готелю
    rooms = get_rooms_by_hotel(db, hotel_id)

    # Отримуємо всі активні бронювання
    active_bookings = (
        db.query(Booking)
        .filter(Booking.status != "cancelled")
        .all()
    )

    # Конвертуємо SQLAlchemy об'єкти в dataclass для перевірки
    # через існуючу функцію utils.is_room_available
    from booking_service.models import Booking as BookingDC

    bookings_dc = [
        BookingDC(
            id=b.id,
            user_id=b.user_id,
            room_id=b.room_id,
            check_in=b.check_in if isinstance(b.check_in, date)
            else b.check_in.date(),
            check_out=b.check_out if isinstance(b.check_out, date)
            else b.check_out.date(),
            total_price=b.total_price,
            status=b.status,
        )
        for b in active_bookings
    ]

    return [
        r for r in rooms
        if check_available(r.id, check_in, check_out, bookings_dc)
    ]


# ── User ──────────────────────────────────────────────────────────────────────


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Повертає користувача за id або None.

    Args:
        db: Активна сесія БД.
        user_id: Ідентифікатор користувача.

    Returns:
        Об'єкт User або None.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Повертає користувача за email або None.

    Args:
        db: Активна сесія БД.
        email: Електронна пошта.

    Returns:
        Об'єкт User або None.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    name: str,
    email: str,
    phone: str = "",
) -> User:
    """Створює нового користувача.

    Args:
        db: Активна сесія БД.
        name: Ім'я.
        email: Email (повинен бути унікальним).
        phone: Телефон.

    Returns:
        Створений об'єкт User.

    Raises:
        ValueError: Якщо користувач з таким email вже існує.
    """
    # Перевіряємо унікальність email
    if get_user_by_email(db, email):
        raise ValueError(f"Користувач з email '{email}' вже існує.")

    user = User(name=name, email=email, phone=phone)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session) -> list[User]:
    """Повертає всіх користувачів.

    Args:
        db: Активна сесія БД.

    Returns:
        Список всіх користувачів.
    """
    return db.query(User).order_by(User.name).all()


# ── Booking ───────────────────────────────────────────────────────────────────


def get_booking_by_id(db: Session, booking_id: int) -> Booking | None:
    """Повертає бронювання за id або None.

    Args:
        db: Активна сесія БД.
        booking_id: Ідентифікатор бронювання.

    Returns:
        Об'єкт Booking або None.
    """
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_bookings_by_user(db: Session, user_id: int) -> list[Booking]:
    """Повертає всі бронювання користувача.

    Args:
        db: Активна сесія БД.
        user_id: Ідентифікатор користувача.

    Returns:
        Список бронювань користувача.
    """
    return (
        db.query(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )


def create_booking(
    db: Session,
    user_id: int,
    room_id: int,
    check_in: date,
    check_out: date,
    total_price: float,
) -> Booking:
    """Створює нове бронювання.

    Args:
        db: Активна сесія БД.
        user_id: Ідентифікатор користувача.
        room_id: Ідентифікатор кімнати.
        check_in: Дата заїзду.
        check_out: Дата виїзду.
        total_price: Загальна вартість.

    Returns:
        Створений об'єкт Booking.
    """
    booking = Booking(
        user_id=user_id,
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        total_price=total_price,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking_id: int) -> Booking | None:
    """Скасовує бронювання — змінює статус на 'cancelled'.

    Args:
        db: Активна сесія БД.
        booking_id: Ідентифікатор бронювання.

    Returns:
        Оновлений об'єкт Booking або None якщо не знайдено.
    """
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        return None

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking


def get_all_bookings(db: Session) -> list[Booking]:
    """Повертає всі бронювання відсортовані від найновіших.

    Args:
        db: Активна сесія БД.

    Returns:
        Список всіх бронювань.
    """
    return (
        db.query(Booking)
        .order_by(Booking.created_at.desc())
        .all()
    )