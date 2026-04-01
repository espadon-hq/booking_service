"""Роутер для операцій з готелями."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from booking_service import repository as repo
from booking_service.database import get_db
from booking_service.schemas import HotelCreate, HotelOut, HotelUpdate, MessageOut

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get(
    "/",
    response_model=list[HotelOut],
    summary="Список всіх готелів",
)
def get_hotels(
    city: str | None = Query(None, description="Фільтр за містом"),
    db: Session = Depends(get_db),
) -> list:
    """Повертає список готелів з необов'язковою фільтрацією за містом.

    Args:
        city: Назва міста для фільтрації.
        db: Сесія БД.

    Returns:
        Список готелів.
    """
    if city:
        return repo.get_hotels_by_city(db, city)
    return repo.get_all_hotels(db)


@router.get(
    "/{hotel_id}",
    response_model=HotelOut,
    summary="Отримати готель за id",
)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """Повертає готель за його id.

    Args:
        hotel_id: Ідентифікатор готелю.
        db: Сесія БД.

    Returns:
        Об'єкт готелю.

    Raises:
        HTTPException 404: Якщо готель не знайдено.
    """
    hotel = repo.get_hotel_by_id(db, hotel_id)
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )
    return hotel


@router.post(
    "/",
    response_model=HotelOut,
    status_code=status.HTTP_201_CREATED,
    summary="Створити готель",
)
def create_hotel(data: HotelCreate, db: Session = Depends(get_db)):
    """Створює новий готель.

    Args:
        data: Валідовані дані нового готелю.
        db: Сесія БД.

    Returns:
        Створений готель.
    """
    return repo.create_hotel(
        db,
        name=data.name,
        city=data.city,
        address=data.address,
        stars=data.stars,
        description=data.description,
    )


@router.patch(
    "/{hotel_id}",
    response_model=HotelOut,
    summary="Оновити готель",
)
def update_hotel(
    hotel_id: int,
    data: HotelUpdate,
    db: Session = Depends(get_db),
):
    """Оновлює поля готелю (лише передані поля).

    Args:
        hotel_id: Ідентифікатор готелю.
        data: Поля для оновлення.
        db: Сесія БД.

    Returns:
        Оновлений готель.

    Raises:
        HTTPException 404: Якщо готель не знайдено.
    """
    # Передаємо лише ті поля що були явно передані (не None)
    updates = data.model_dump(exclude_none=True)
    hotel = repo.update_hotel(db, hotel_id, **updates)

    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )
    return hotel


@router.delete(
    "/{hotel_id}",
    response_model=MessageOut,
    summary="Видалити готель",
)
def delete_hotel(hotel_id: int, db: Session = Depends(get_db)):
    """Видаляє готель разом з кімнатами та бронюваннями.

    Args:
        hotel_id: Ідентифікатор готелю.
        db: Сесія БД.

    Returns:
        Повідомлення про успішне видалення.

    Raises:
        HTTPException 404: Якщо готель не знайдено.
    """
    deleted = repo.delete_hotel(db, hotel_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Готель з id={hotel_id} не знайдено.",
        )
    return {"message": f"Готель #{hotel_id} видалено."}