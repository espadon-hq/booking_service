"""SQLAlchemy моделі таблиць бази даних.

Лаб 4 — замінюємо dataclass на повноцінні ORM моделі.
Структура сутностей та сама що і в Лаб 1, але тепер
дані зберігаються в PostgreSQL.
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from booking_service.database import Base


class Hotel(Base):
    """Модель таблиці готелів.

    Attributes:
        id: Первинний ключ, автоінкремент.
        name: Назва готелю.
        city: Місто розташування.
        address: Повна адреса.
        stars: Кількість зірок від 1 до 5.
        description: Опис готелю.
        created_at: Дата створення запису.
        rooms: Зв'язок один-до-багатьох з кімнатами.
    """

    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    stars: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("stars >= 1 AND stars <= 5", name="check_stars"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Зв'язок з кімнатами — cascade видаляє кімнати разом з готелем
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Рядкове представлення для дебагу."""
        return f"<Hotel id={self.id} name={self.name!r} city={self.city!r}>"

    def __str__(self) -> str:
        """Зручне рядкове представлення."""
        return f"[{self.stars}*] {self.name} — {self.city}"


class Room(Base):
    """Модель таблиці кімнат.

    Attributes:
        id: Первинний ключ, автоінкремент.
        hotel_id: Зовнішній ключ на готель.
        number: Номер кімнати.
        room_type: Тип кімнати — single, double, suite.
        price_per_night: Ціна за ніч у гривнях.
        capacity: Максимальна кількість гостей.
        hotel: Зв'язок з готелем.
        bookings: Зв'язок з бронюваннями.
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
    )
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    # Зв'язки
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="rooms")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Рядкове представлення для дебагу."""
        return (
            f"<Room id={self.id} number={self.number!r} "
            f"type={self.room_type!r} price={self.price_per_night}>"
        )

    def __str__(self) -> str:
        """Зручне рядкове представлення."""
        return (
            f"Кімната {self.number} ({self.room_type})"
            f" — {self.price_per_night} грн/ніч"
        )


class User(Base):
    """Модель таблиці користувачів.

    Attributes:
        id: Первинний ключ, автоінкремент.
        name: Повне ім'я.
        email: Унікальна електронна пошта.
        phone: Номер телефону.
        created_at: Дата реєстрації.
        bookings: Зв'язок з бронюваннями.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # unique=True — email повинен бути унікальним в системі
    email: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True
    )
    phone: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Рядкове представлення для дебагу."""
        return f"<User id={self.id} email={self.email!r}>"

    def __str__(self) -> str:
        """Зручне рядкове представлення."""
        return f"{self.name} <{self.email}>"


class Booking(Base):
    """Модель таблиці бронювань.

    Attributes:
        id: Первинний ключ, автоінкремент.
        user_id: Зовнішній ключ на користувача.
        room_id: Зовнішній ключ на кімнату.
        check_in: Дата заїзду.
        check_out: Дата виїзду.
        total_price: Загальна вартість бронювання.
        status: Статус — pending, confirmed, cancelled.
        created_at: Дата створення бронювання.
        user: Зв'язок з користувачем.
        room: Зв'язок з кімнатою.
    """

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    check_in: Mapped[date] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    check_out: Mapped[date] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Зв'язки з користувачем та кімнатою
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")

    def nights(self) -> int:
        """Повертає кількість ночей бронювання."""
        if isinstance(self.check_in, datetime):
            check_in = self.check_in.date()
            check_out = self.check_out.date()
        else:
            check_in = self.check_in
            check_out = self.check_out
        return (check_out - check_in).days

    def __repr__(self) -> str:
        """Рядкове представлення для дебагу."""
        return (
            f"<Booking id={self.id} user_id={self.user_id} "
            f"room_id={self.room_id} status={self.status!r}>"
        )

    def __str__(self) -> str:
        """Зручне рядкове представлення."""
        return (
            f"Бронювання #{self.id} | "
            f"{self.check_in} — {self.check_out} | "
            f"{self.total_price} грн | {self.status}"
        )