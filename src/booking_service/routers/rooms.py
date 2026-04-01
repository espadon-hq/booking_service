"""Роутер для операцій з кімнатами."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from booking_service import repository as repo
from booking_service.database import get_db
from booking_service.models import Room as RoomDC
from booking_service.schemas import (
    MessageOut,
    RoomAvailabilityOut,
    RoomCreate,
    RoomOut,
)
from booking_service.utils import calculate_total_price, is_dates_valid

router = APIRouter(prefix="/hotels/{hotel_id}/rooms", tags=["rooms"])


@router.get(
    "/",
    response_model=list[RoomOut],
    summary="Кімнати готелю",
)
def get_rooms(hotel_id: int, db: Session = Depends(get_db)):
    """Повертає всі кімнати готелю.

    Args:
        hotel_id: Ідентифікатор готелю.
        db: Сесія БД.

    Returns:
        Список кімнат.

    Raises:
        HTTPException 404: Якщо готель не знайдено.
    """
    if not repo.get_hotel_by_id(db, hotel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )
    return repo.get_rooms_by_hotel(db, hotel_id)


@router.get(
    "/available",
    response_model=list[RoomAvailabilityOut],
    summary="Вільні кімнати на дати",
)
def get_available_rooms(
    hotel_id: int,
    check_in: date = Query(..., description="Дата заїзду РРРР-ММ-ДД"),
    check_out: date = Query(..., description="Дата виїзду РРРР-ММ-ДД"),
    db: Session = Depends(get_db),
):
    """Повертає вільні кімнати готелю на вказані дати.

    Args:
        hotel_id: Ідентифікатор готелю.
        check_in: Дата заїзду.
        check_out: Дата виїзду.
        db: Сесія БД.

    Returns:
        Список вільних кімнат з вартістю.

    Raises:
        HTTPException 400: Якщо дати некоректні.
        HTTPException 404: Якщо готель не знайдено.
    """
    if not repo.get_hotel_by_id(db, hotel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )

    if not is_dates_valid(check_in, check_out):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некоректні дати. Заїзд — сьогодні або пізніше, виїзд — після заїзду.",
        )

    nights = (check_out - check_in).days
    available_rooms = repo.get_available_rooms(db, hotel_id, check_in, check_out)

    result = []
    for room in available_rooms:
        # Конвертуємо в dataclass для calculate_total_price
        room_dc = RoomDC(
            id=room.id,
            hotel_id=room.hotel_id,
            number=room.number,
            room_type=room.room_type,
            price_per_night=room.price_per_night,
            capacity=room.capacity,
        )
        total = calculate_total_price(room_dc, check_in, check_out)
        result.append({
            "id": room.id,
            "hotel_id": room.hotel_id,
            "number": room.number,
            "room_type": room.room_type,
            "price_per_night": room.price_per_night,
            "capacity": room.capacity,
            "available": True,
            "total_price": total,
            "nights": nights,
        })

    return result


@router.get(
    "/{room_id}",
    response_model=RoomOut,
    summary="Отримати кімнату за id",
)
def get_room(
    hotel_id: int,
    room_id: int,
    db: Session = Depends(get_db),
):
    """Повертає кімнату за id.

    Args:
        hotel_id: Ідентифікатор готелю.
        room_id: Ідентифікатор кімнати.
        db: Сесія БД.

    Returns:
        Об'єкт кімнати.

    Raises:
        HTTPException 404: Якщо кімната не знайдена.
    """
    room = repo.get_room_by_id(db, room_id)
    if not room or room.hotel_id != hotel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кімната з id={room_id} не знайдена.",
        )
    return room


@router.post(
    "/",
    response_model=RoomOut,
    status_code=status.HTTP_201_CREATED,
    summary="Додати кімнату до готелю",
)
def create_room(
    hotel_id: int,
    data: RoomCreate,
    db: Session = Depends(get_db),
):
    """Додає нову кімнату до готелю.

    Args:
        hotel_id: Ідентифікатор готелю.
        data: Дані нової кімнати.
        db: Сесія БД.

    Returns:
        Створена кімната.

    Raises:
        HTTPException 404: Якщо готель не знайдено.
    """
    if not repo.get_hotel_by_id(db, hotel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )
    return repo.create_room(
        db,
        hotel_id=hotel_id,
        number=data.number,
        room_type=data.room_type,
        price_per_night=data.price_per_night,
        capacity=data.capacity,
    )


@router.delete(
    "/{room_id}",
    response_model=MessageOut,
    summary="Видалити кімнату",
)
def delete_room(
    hotel_id: int,
    room_id: int,
    db: Session = Depends(get_db),
):
    """Видаляє кімнату з готелю.

    Args:
        hotel_id: Ідентифікатор готелю.
        room_id: Ідентифікатор кімнати.
        db: Сесія БД.

    Returns:
        Повідомлення про видалення.

    Raises:
        HTTPException 404: Якщо кімната не знайдена.
    """
    room = repo.get_room_by_id(db, room_id)
    if not room or room.hotel_id != hotel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Кімната з id={room_id} не знайдена.",
        )
    repo.delete_room(db, room_id)
    return {"message": f"Кімната #{room_id} видалена."}