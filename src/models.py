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
    rooms: List[Room] = field(default_factory=list)

@dataclass
class Booking:
    id: int
    user_name: str
    room_id: int
    hotel_name: str
    check_in: date
    check_out: date
    total_price: float