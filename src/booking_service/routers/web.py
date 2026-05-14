"""Веб-інтерфейс (Jinja2 шаблони)."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from booking_service import repository as repo
from booking_service.database import get_db
from booking_service.repository import calculate_total_price, is_room_available

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="src/booking_service/templates")


@router.get("/", response_class=HTMLResponse)
def hotels_list(request: Request, city: str = None, db: Session = Depends(get_db)):
    hotels = repo.get_hotels_by_city(db, city) if city else repo.get_all_hotels(db)
    return templates.TemplateResponse(request, "hotels.html", {"hotels": hotels, "city": city})


@router.get("/ui/hotels/{hotel_id}", response_class=HTMLResponse)
def hotel_detail(
    request: Request,
    hotel_id: int,
    check_in: str = None,
    check_out: str = None,
    db: Session = Depends(get_db),
):
    hotel = repo.get_hotel_by_id(db, hotel_id)
    if not hotel:
        return HTMLResponse("Готель не знайдено", status_code=404)

    today = date.today()
    if not check_in:
        check_in = str(today + timedelta(days=1))
    if not check_out:
        check_out = str(today + timedelta(days=4))

    rooms = []
    error = None

    try:
        ci = date.fromisoformat(check_in)
        co = date.fromisoformat(check_out)
        if co <= ci:
            error = "Дата виїзду має бути після дати заїзду."
            ci = co = None
    except ValueError:
        error = "Невірний формат дати."
        ci = co = None

    for room in repo.get_rooms_by_hotel(db, hotel_id):
        available = total_price = None
        if ci and co:
            bookings = repo.get_bookings_by_room(db, room.id)
            available = is_room_available(room.id, ci, co, bookings)
            if available:
                total_price = calculate_total_price(room, ci, co)
        rooms.append({"room": room, "available": available, "total_price": total_price})

    return templates.TemplateResponse(request, "hotel_detail.html", {
        "hotel": hotel, "rooms": rooms,
        "check_in": check_in, "check_out": check_out, "error": error,
    })


@router.post("/bookings/create")
def create_booking(
    room_id: int = Form(...),
    hotel_id: int = Form(...),
    email: str = Form(...),
    check_in: str = Form(...),
    check_out: str = Form(...),
    db: Session = Depends(get_db),
):
    user = repo.get_user_by_email(db, email) or repo.create_user(db, name=email.split("@")[0], email=email)
    try:
        ci, co = date.fromisoformat(check_in), date.fromisoformat(check_out)
        room = repo.get_room_by_id(db, room_id)
        total = calculate_total_price(room, ci, co)
        repo.create_booking(db, user_id=user.id, room_id=room_id, check_in=ci, check_out=co, total_price=total)
    except Exception:
        pass
    return RedirectResponse(f"/ui/hotels/{hotel_id}?check_in={check_in}&check_out={check_out}", status_code=303)


@router.get("/ui/bookings", response_class=HTMLResponse)
def bookings_list(request: Request, db: Session = Depends(get_db)):
    result = []
    for b in repo.get_all_bookings(db):
        room = repo.get_room_by_id(db, b.room_id)
        hotel = repo.get_hotel_by_id(db, room.hotel_id) if room else None
        user = repo.get_user_by_id(db, b.user_id)
        result.append({
            "id": b.id,
            "hotel_name": hotel.name if hotel else "-",
            "room_number": room.number if room else "-",
            "user_email": user.email if user else "-",
            "check_in": b.check_in,
            "check_out": b.check_out,
            "total_price": b.total_price,
            "status": b.status,
        })
    return templates.TemplateResponse(request, "bookings.html", {"bookings": result})


@router.post("/ui/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    repo.cancel_booking(db, booking_id)
    return RedirectResponse("/ui/bookings", status_code=303)