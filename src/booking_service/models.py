from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Room:
    id: int
    price_per_night: float
    room_type: str

@dataclass
class Hotel:
    id: int
    name: str
    location: str
    price: float  # додаємо ціну для спрощення логіки engine
    rooms: List[Room] = field(default_factory=list)

@dataclass
class Booking:
    id: int
    user_name: str
    hotel_id: int
    check_in: date
    check_out: date
    total_price: float