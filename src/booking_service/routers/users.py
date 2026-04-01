"""Роутер для операцій з користувачами."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from booking_service import repository as repo
from booking_service.database import get_db
from booking_service.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserOut],
    summary="Список користувачів",
)
def get_users(db: Session = Depends(get_db)):
    """Повертає список всіх користувачів.

    Args:
        db: Сесія БД.

    Returns:
        Список користувачів.
    """
    return repo.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Отримати користувача за id",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Повертає користувача за id.

    Args:
        user_id: Ідентифікатор користувача.
        db: Сесія БД.

    Returns:
        Об'єкт користувача.

    Raises:
        HTTPException 404: Якщо користувача не знайдено.
    """
    user = repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з id={user_id} не знайдено.",
        )
    return user


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Зареєструвати користувача",
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Реєструє нового користувача.

    Args:
        data: Дані нового користувача.
        db: Сесія БД.

    Returns:
        Створений користувач.

    Raises:
        HTTPException 409: Якщо email вже зайнятий.
    """
    try:
        return repo.create_user(
            db,
            name=data.name,
            email=data.email,
            phone=data.phone,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{user_id}/bookings",
    summary="Бронювання користувача",
)
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    """Повертає всі бронювання користувача.

    Args:
        user_id: Ідентифікатор користувача.
        db: Сесія БД.

    Returns:
        Список бронювань.

    Raises:
        HTTPException 404: Якщо користувача не знайдено.
    """
    if not repo.get_user_by_id(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з id={user_id} не знайдено.",
        )

    bookings = repo.get_bookings_by_user(db, user_id)

    # Збагачуємо дані деталями готелю та кімнати
    result = []
    for b in bookings:
        room = repo.get_room_by_id(db, b.room_id)
        hotel = repo.get_hotel_by_id(db, room.hotel_id) if room else None
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "room_id": b.room_id,
            "check_in": b.check_in,
            "check_out": b.check_out,
            "total_price": b.total_price,
            "status": b.status,
            "created_at": b.created_at,
            "hotel_name": hotel.name if hotel else None,
            "room_number": room.number if room else None,
            "nights": b.nights(),
        })

    return result