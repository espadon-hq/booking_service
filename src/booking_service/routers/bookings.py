"""Роутер для операцій з бронюваннями."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from booking_service import repository as repo
from booking_service.database import get_db
from booking_service.models import Booking as BookingDC
from booking_service.models import Room as RoomDC
from booking_service.schemas import BookingCreate, BookingOut, MessageOut
from booking_service.utils import (
    calculate_total_price,
    is_dates_valid,
    is_room_available,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get(
    "/",
    response_model=list[BookingOut],
    summary="Список всіх бронювань",
)
def get_bookings(db: Session = Depends(get_db)):
    """Повертає список всіх бронювань.

    Args:
        db: Сесія БД.

    Returns:
        Список бронювань.
    """
    return repo.get_all_bookings(db)


@router.get(
    "/{booking_id}",
    response_model=BookingOut,
    summary="Отримати бронювання за id",
)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """Повертає бронювання за id.

    Args:
        booking_id: Ідентифікатор бронювання.
        db: Сесія БД.

    Returns:
        Об'єкт бронювання.

    Raises:
        HTTPException 404: Якщо бронювання не знайдено.
    """
    booking = repo.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронювання з id={booking_id} не знайдено.",
        )
    return booking


@router.post(
    "/",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Створити бронювання",
)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    """Створює нове бронювання кімнати.

    Перевіряє:
        - Існування користувача та кімнати.
        - Коректність дат.
        - Доступність кімнати на вказані дати.

    Args:
        data: Дані бронювання.
        db: Сесія БД.

    Returns:
        Створене бронювання.

    Raises:
        HTTPException 400: Якщо дати некоректні або кімната зайнята.
        HTTPException 404: Якщо користувач або кімната не знайдені.
    """
    # Перевіряємо існування користувача
    if not repo.get_user_by_id(db, data.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з id={data.user_id} не знайдено.",
        )

    # Перевіряємо існування кімнати
    room = repo.get_room_by_id(db, data.room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кімнату з id={data.room_id} не знайдено.",
        )

    # Перевіряємо коректність дат
    if not is_dates_valid(data.check_in, data.check_out):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некоректні дати бронювання.",
        )

    # Отримуємо активні бронювання для перевірки доступності
    all_bookings = repo.get_all_bookings(db)

    # Конвертуємо в dataclass для is_room_available
    bookings_dc = [
        BookingDC(
            id=b.id,
            user_id=b.user_id,
            room_id=b.room_id,
            check_in=b.check_in if not hasattr(b.check_in, "date")
            else b.check_in.date(),
            check_out=b.check_out if not hasattr(b.check_out, "date")
            else b.check_out.date(),
            total_price=b.total_price,
            status=b.status,
        )
        for b in all_bookings
    ]

    # Перевіряємо доступність кімнати
    if not is_room_available(
        data.room_id, data.check_in, data.check_out, bookings_dc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кімната вже зайнята на вказані дати.",
        )

    # Розраховуємо вартість
    room_dc = RoomDC(
        id=room.id,
        hotel_id=room.hotel_id,
        number=room.number,
        room_type=room.room_type,
        price_per_night=room.price_per_night,
        capacity=room.capacity,
    )
    total_price = calculate_total_price(room_dc, data.check_in, data.check_out)

    return repo.create_booking(
        db,
        user_id=data.user_id,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out,
        total_price=total_price,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=MessageOut,
    summary="Скасувати бронювання",
)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Скасовує бронювання.

    Args:
        booking_id: Ідентифікатор бронювання.
        db: Сесія БД.

    Returns:
        Повідомлення про скасування.

    Raises:
        HTTPException 404: Якщо бронювання не знайдено.
        HTTPException 400: Якщо бронювання вже скасовано.
    """
    booking = repo.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронювання з id={booking_id} не знайдено.",
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Бронювання вже скасовано.",
        )

    repo.cancel_booking(db, booking_id)
    return {"message": f"Бронювання #{booking_id} скасовано."}