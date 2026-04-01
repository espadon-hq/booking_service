"""Головний модуль FastAPI застосунку.

Лаб 5 — REST API точка входу.
"""

from fastapi import FastAPI

from booking_service.database import init_db
from booking_service.routers import bookings, hotels, rooms, users

app = FastAPI(
    title="Booking Service API",
    description="REST API для онлайн-бронювання готелів.",
    version="0.0.1",
)


@app.on_event("startup")
def startup() -> None:
    """Створює таблиці в БД при старті застосунку."""
    init_db()


# Підключаємо всі роутери
app.include_router(hotels.router)
app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(bookings.router)


@app.get("/", tags=["root"])
def root() -> dict:
    """Перевірка що API працює."""
    return {"message": "Booking Service API працює!", "version": "0.0.1"}