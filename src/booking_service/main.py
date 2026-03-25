"""Консольний інтерфейс системи бронювання готелів.

Лаб 1 — взаємодія з користувачем через термінал.
Без БД та API — дані зберігаються в пам'яті під час сесії.
"""

import os
from datetime import date

from dotenv import load_dotenv

from booking_service.models import Booking, Hotel, Room, User
from booking_service.utils import (
    calculate_total_price,
    filter_hotels_by_city,
    filter_rooms_by_price,
    is_dates_valid,
    is_room_available,
)

load_dotenv()

# ── Початкові дані ────────────────────────────────────────────────────────────

HOTELS: list[Hotel] = [
    Hotel(1, "Grand Hotel", "Київ", "вул. Хрещатик, 1", 5,
          "Розкішний готель у центрі міста"),
    Hotel(2, "City Inn", "Київ", "вул. Велика Васильківська, 10", 3,
          "Затишний готель для ділових поїздок"),
    Hotel(3, "Sea View", "Одеса", "Приморський бульвар, 5", 4,
          "Готель з видом на море"),
]

ROOMS: list[Room] = [
    Room(1, 1, "101", "single", 1500.0, 1),
    Room(2, 1, "202", "double", 2500.0, 2),
    Room(3, 1, "301", "suite", 5000.0, 4),
    Room(4, 2, "101", "single", 900.0, 1),
    Room(5, 2, "102", "double", 1800.0, 2),
    Room(6, 3, "201", "double", 2200.0, 2),
    Room(7, 3, "301", "suite", 4500.0, 3),
]

BOOKINGS: list[Booking] = []
USERS: list[User] = []


# ── Допоміжні функції ─────────────────────────────────────────────────────────


def clear() -> None:
    """Очищає екран терміналу."""
    os.system("cls" if os.name == "nt" else "clear")


def sep(title: str = "") -> None:
    """Виводить розділювач з необов'язковим заголовком."""
    print("\n" + "─" * 50)
    if title:
        print(f"  {title}")
        print("─" * 50)


def pause() -> None:
    """Зупиняє виконання до натискання Enter."""
    input("\n  Натисніть Enter для продовження...")


def input_int(prompt: str, min_val: int = 1, max_val: int = 9999) -> int | None:
    """Зчитує ціле число від користувача з валідацією.

    Args:
        prompt: Текст запиту.
        min_val: Мінімально допустиме значення.
        max_val: Максимально допустиме значення.

    Returns:
        Введене число або None якщо введення некоректне.
    """
    try:
        value = int(input(prompt))
        if min_val <= value <= max_val:
            return value
        print(f"  Введіть число від {min_val} до {max_val}.")
        return None
    except ValueError:
        print("  Некоректне введення. Очікується ціле число.")
        return None


def input_date(prompt: str) -> date | None:
    """Зчитує дату у форматі РРРР-ММ-ДД.

    Args:
        prompt: Текст запиту.

    Returns:
        Об'єкт date або None якщо формат некоректний.
    """
    raw = input(prompt).strip()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        print("  Некоректний формат. Використовуйте РРРР-ММ-ДД.")
        return None


def get_hotel_by_id(hotel_id: int) -> Hotel | None:
    """Повертає готель за id або None якщо не знайдено."""
    return next((h for h in HOTELS if h.id == hotel_id), None)


def get_room_by_id(room_id: int) -> Room | None:
    """Повертає кімнату за id або None якщо не знайдено."""
    return next((r for r in ROOMS if r.id == room_id), None)


def get_user_by_id(user_id: int) -> User | None:
    """Повертає користувача за id або None якщо не знайдено."""
    return next((u for u in USERS if u.id == user_id), None)


def next_id(items: list) -> int:
    """Генерує наступний вільний id для списку об'єктів."""
    return max((i.id for i in items), default=0) + 1


# ── Розділи меню ──────────────────────────────────────────────────────────────


def show_hotels() -> None:
    """Показує список готелів з необов'язковою фільтрацією за містом."""
    sep("ГОТЕЛІ")

    city = input("  Фільтр за містом (або Enter для всіх): ").strip()
    hotels = filter_hotels_by_city(HOTELS, city) if city else HOTELS

    if not hotels:
        print(f"  Готелів у місті '{city}' не знайдено.")
        pause()
        return

    print()
    for h in hotels:
        print(f"  #{h.id}  {h}")
        print(f"       Адреса: {h.address}")
        if h.description:
            print(f"       {h.description}")
        print()

    pause()


def show_rooms() -> None:
    """Показує кімнати обраного готелю з фільтром за ціною."""
    sep("КІМНАТИ")

    for h in HOTELS:
        print(f"  #{h.id}  {h}")

    hotel_id = input_int("\n  Оберіть готель (id): ")
    if hotel_id is None:
        pause()
        return

    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        print("  Готель не знайдено.")
        pause()
        return

    max_price_input = input(
        "  Максимальна ціна за ніч (або Enter без фільтру): "
    ).strip()

    rooms = [r for r in ROOMS if r.hotel_id == hotel_id]

    if max_price_input:
        try:
            max_price = float(max_price_input)
            rooms = filter_rooms_by_price(rooms, max_price)
        except ValueError:
            print("  Некоректна ціна, фільтр не застосовано.")

    if not rooms:
        print(f"\n  У готелі '{hotel.name}' немає кімнат за вказаними критеріями.")
        pause()
        return

    sep(f"КІМНАТИ — {hotel.name}")
    for r in rooms:
        print(f"  #{r.id}  {r} | місць: {r.capacity}")

    pause()


def check_availability() -> None:
    """Перевіряє доступність кімнат готелю на вказані дати."""
    sep("ПЕРЕВІРКА ДОСТУПНОСТІ")

    for h in HOTELS:
        print(f"  #{h.id}  {h}")

    hotel_id = input_int("\n  Оберіть готель (id): ")
    if hotel_id is None:
        pause()
        return

    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        print("  Готель не знайдено.")
        pause()
        return

    check_in = input_date("  Дата заїзду (РРРР-ММ-ДД): ")
    if check_in is None:
        pause()
        return

    check_out = input_date("  Дата виїзду (РРРР-ММ-ДД): ")
    if check_out is None:
        pause()
        return

    if not is_dates_valid(check_in, check_out):
        print("  Некоректні дати.")
        pause()
        return

    rooms = [r for r in ROOMS if r.hotel_id == hotel_id]
    nights = (check_out - check_in).days

    sep(f"ДОСТУПНІСТЬ — {hotel.name} | {check_in} — {check_out}")

    available_count = 0
    for r in rooms:
        available = is_room_available(r.id, check_in, check_out, BOOKINGS)
        status = "вільна  ✓" if available else "зайнята ✗"
        total = r.price_per_night * nights
        print(
            f"  #{r.id}  Кімната {r.number} ({r.room_type}) | "
            f"{r.price_per_night} грн/ніч | "
            f"{total} грн за {nights} ніч | {status}"
        )
        if available:
            available_count += 1

    print(f"\n  Вільних кімнат: {available_count} з {len(rooms)}")
    pause()


def register_user() -> None:
    """Реєструє нового користувача в системі."""
    sep("РЕЄСТРАЦІЯ")

    name = input("  Ім'я та прізвище: ").strip()
    if not name:
        print("  Ім'я не може бути порожнім.")
        pause()
        return

    email = input("  Email: ").strip()
    if not email or "@" not in email:
        print("  Некоректний email.")
        pause()
        return

    phone = input("  Телефон (або Enter): ").strip()

    user = User(
        id=next_id(USERS),
        name=name,
        email=email,
        phone=phone,
    )
    USERS.append(user)
    print(f"\n  Зареєстровано! Ваш id: {user.id}")
    pause()


def create_booking() -> None:
    """Створює нове бронювання кімнати."""
    sep("НОВЕ БРОНЮВАННЯ")

    if not USERS:
        print("  Спочатку зареєструйтесь (пункт 4 меню).")
        pause()
        return

    # Вибір користувача
    print("  Користувачі:")
    for u in USERS:
        print(f"  #{u.id}  {u}")

    user_id = input_int("\n  Ваш id: ")
    if user_id is None:
        pause()
        return

    user = get_user_by_id(user_id)
    if not user:
        print("  Користувача не знайдено.")
        pause()
        return

    # Вибір готелю
    sep("Оберіть готель")
    for h in HOTELS:
        print(f"  #{h.id}  {h}")

    hotel_id = input_int("\n  id готелю: ")
    if hotel_id is None:
        pause()
        return

    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        print("  Готель не знайдено.")
        pause()
        return

    # Введення дат
    check_in = input_date("  Дата заїзду (РРРР-ММ-ДД): ")
    if check_in is None:
        pause()
        return

    check_out = input_date("  Дата виїзду (РРРР-ММ-ДД): ")
    if check_out is None:
        pause()
        return

    if not is_dates_valid(check_in, check_out):
        print("  Некоректні дати.")
        pause()
        return

    # Вільні кімнати
    rooms = [r for r in ROOMS if r.hotel_id == hotel_id]
    available_rooms = [
        r for r in rooms
        if is_room_available(r.id, check_in, check_out, BOOKINGS)
    ]

    if not available_rooms:
        print(f"\n  У готелі '{hotel.name}' немає вільних кімнат на ці дати.")
        pause()
        return

    nights = (check_out - check_in).days
    sep("Вільні кімнати")
    for r in available_rooms:
        total = r.price_per_night * nights
        print(
            f"  #{r.id}  Кімната {r.number} ({r.room_type}) | "
            f"{r.price_per_night} грн/ніч | {total} грн за {nights} ніч(ей)"
        )

    room_id = input_int("\n  Оберіть кімнату (id): ")
    if room_id is None:
        pause()
        return

    room = get_room_by_id(room_id)
    if not room or room.hotel_id != hotel_id:
        print("  Кімнату не знайдено.")
        pause()
        return

    if not is_room_available(room.id, check_in, check_out, BOOKINGS):
        print("  Ця кімната вже зайнята на вказані дати.")
        pause()
        return

    # Підтвердження
    total_price = calculate_total_price(room, check_in, check_out)

    sep("Підтвердження")
    print(f"  Готель  : {hotel.name}")
    print(f"  Кімната : {room.number} ({room.room_type})")
    print(f"  Заїзд   : {check_in}")
    print(f"  Виїзд   : {check_out}")
    print(f"  Ночей   : {nights}")
    print(f"  Вартість: {total_price} грн")

    confirm = input("\n  Підтвердити? (так/ні): ").strip().lower()
    if confirm not in ("так", "т", "yes", "y"):
        print("  Бронювання скасовано.")
        pause()
        return

    booking = Booking(
        id=next_id(BOOKINGS),
        user_id=user.id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        total_price=total_price,
        status="confirmed",
    )
    BOOKINGS.append(booking)
    print(f"\n  Бронювання підтверджено! #{booking.id}")
    pause()


def show_my_bookings() -> None:
    """Показує всі бронювання обраного користувача."""
    sep("МОЇ БРОНЮВАННЯ")

    if not USERS:
        print("  Користувачів ще немає.")
        pause()
        return

    for u in USERS:
        print(f"  #{u.id}  {u}")

    user_id = input_int("\n  Ваш id: ")
    if user_id is None:
        pause()
        return

    user = get_user_by_id(user_id)
    if not user:
        print("  Користувача не знайдено.")
        pause()
        return

    my_bookings = [b for b in BOOKINGS if b.user_id == user_id]

    if not my_bookings:
        print(f"\n  У {user.name} ще немає бронювань.")
        pause()
        return

    sep(f"Бронювання — {user.name}")
    for b in my_bookings:
        room = get_room_by_id(b.room_id)
        hotel = (
            next((h for h in HOTELS if h.id == room.hotel_id), None)
            if room else None
        )
        print(
            f"  #{b.id}  {hotel.name if hotel else '?'} | "
            f"кімната {room.number if room else '?'} | "
            f"{b.check_in} — {b.check_out} | "
            f"{b.total_price} грн | {b.status}"
        )

    pause()


def cancel_booking() -> None:
    """Скасовує активне бронювання."""
    sep("СКАСУВАННЯ БРОНЮВАННЯ")

    active = [b for b in BOOKINGS if b.status != "cancelled"]

    if not active:
        print("  Немає активних бронювань.")
        pause()
        return

    for b in active:
        room = get_room_by_id(b.room_id)
        hotel = (
            next((h for h in HOTELS if h.id == room.hotel_id), None)
            if room else None
        )
        print(
            f"  #{b.id}  {hotel.name if hotel else '?'} | "
            f"кімната {room.number if room else '?'} | "
            f"{b.check_in} — {b.check_out} | {b.total_price} грн"
        )

    booking_id = input_int("\n  id бронювання для скасування: ")
    if booking_id is None:
        pause()
        return

    booking = next((b for b in BOOKINGS if b.id == booking_id), None)
    if not booking:
        print("  Бронювання не знайдено.")
        pause()
        return

    if booking.status == "cancelled":
        print("  Це бронювання вже скасовано.")
        pause()
        return

    confirm = input("  Скасувати? (так/ні): ").strip().lower()
    if confirm not in ("так", "т", "yes", "y"):
        print("  Дію скасовано.")
        pause()
        return

    booking.status = "cancelled"
    print(f"\n  Бронювання #{booking.id} скасовано.")
    pause()

def export_data() -> None:
    """Експортує всі дані в файли."""
    from booking_service.file_handler import (
        export_bookings_csv,
        export_hotels_csv,
        export_json,
        export_rooms_csv,
    )

    sep("ЕКСПОРТ ДАНИХ")
    print("  1. CSV (окремі файли)")
    print("  2. JSON (один файл)")

    choice = input("\n  Формат: ").strip()

    if choice == "1":
        export_hotels_csv(HOTELS, "data/hotels.csv")
        export_rooms_csv(ROOMS, "data/rooms.csv")
        export_bookings_csv(BOOKINGS, "data/bookings.csv")
        print("\n  Збережено: data/hotels.csv, data/rooms.csv, data/bookings.csv")

    elif choice == "2":
        export_json(HOTELS, ROOMS, BOOKINGS, USERS, "data/backup.json")
        print("\n  Збережено: data/backup.json")

    else:
        print("  Невідомий формат.")

    pause()


def import_data() -> None:
    """Імпортує дані з файлів."""
    from booking_service.file_handler import import_hotels_csv, import_json

    sep("ІМПОРТ ДАНИХ")
    print("  1. Готелі з CSV")
    print("  2. Всі дані з JSON")

    choice = input("\n  Формат: ").strip()

    if choice == "1":
        filepath = input("  Шлях до CSV файлу: ").strip()
        try:
            imported = import_hotels_csv(filepath)
            HOTELS.clear()
            HOTELS.extend(imported)
            print(f"\n  Імпортовано {len(imported)} готелів.")
        except (FileNotFoundError, ValueError) as e:
            print(f"\n  Помилка: {e}")

    elif choice == "2":
        filepath = input("  Шлях до JSON файлу: ").strip()
        try:
            from booking_service.file_handler import import_json
            data = import_json(filepath)
            HOTELS.clear()
            HOTELS.extend(data["hotels"])
            ROOMS.clear()
            ROOMS.extend(data["rooms"])
            BOOKINGS.clear()
            BOOKINGS.extend(data["bookings"])
            USERS.clear()
            USERS.extend(data["users"])
            print(f"\n  Імпортовано: {len(data['hotels'])} готелів, "
                  f"{len(data['rooms'])} кімнат, "
                  f"{len(data['bookings'])} бронювань.")
        except (FileNotFoundError, ValueError) as e:
            print(f"\n  Помилка: {e}")

    else:
        print("  Невідомий формат.")

    pause()
# ── Головне меню ──────────────────────────────────────────────────────────────


def main() -> None:
    """Головна функція — точка входу консольного застосунку."""
    app_name = os.getenv("APP_NAME", "Booking Service")
    app_version = os.getenv("APP_VERSION", "0.0.1")

menu_items = {
    "1": ("Переглянути готелі", show_hotels),
    "2": ("Переглянути кімнати готелю", show_rooms),
    "3": ("Перевірити доступність кімнат", check_availability),
    "4": ("Реєстрація", register_user),
    "5": ("Забронювати кімнату", create_booking),
    "6": ("Мої бронювання", show_my_bookings),
    "7": ("Скасувати бронювання", cancel_booking),
    "8": ("Експорт даних", export_data),
    "9": ("Імпорт даних", import_data),
    "0": ("Вийти", None),
}

    while True:
        clear()
        print(f"\n  {app_name} v{app_version}")
        sep("ГОЛОВНЕ МЕНЮ")

        for key, (title, _) in menu_items.items():
            print(f"  {key}.  {title}")

        choice = input("\n  Ваш вибір: ").strip()

        if choice == "0":
            print("\n  До побачення!\n")
            break

        if choice not in menu_items:
            print("  Невідомий пункт меню.")
            pause()
            continue

        _, action = menu_items[choice]
        action()


def export_data() -> None:
    """Експортує всі дані в файли."""
    from booking_service.file_handler import (
        export_bookings_csv,
        export_hotels_csv,
        export_json,
        export_rooms_csv,
    )

    sep("ЕКСПОРТ ДАНИХ")
    print("  1. CSV (окремі файли)")
    print("  2. JSON (один файл)")

    choice = input("\n  Формат: ").strip()

    if choice == "1":
        export_hotels_csv(HOTELS, "data/hotels.csv")
        export_rooms_csv(ROOMS, "data/rooms.csv")
        export_bookings_csv(BOOKINGS, "data/bookings.csv")
        print("\n  Збережено: data/hotels.csv, data/rooms.csv, data/bookings.csv")

    elif choice == "2":
        export_json(HOTELS, ROOMS, BOOKINGS, USERS, "data/backup.json")
        print("\n  Збережено: data/backup.json")

    else:
        print("  Невідомий формат.")

    pause()


def import_data() -> None:
    """Імпортує дані з файлів."""
    from booking_service.file_handler import import_hotels_csv, import_json

    sep("ІМПОРТ ДАНИХ")
    print("  1. Готелі з CSV")
    print("  2. Всі дані з JSON")

    choice = input("\n  Формат: ").strip()

    if choice == "1":
        filepath = input("  Шлях до CSV файлу: ").strip()
        try:
            imported = import_hotels_csv(filepath)
            HOTELS.clear()
            HOTELS.extend(imported)
            print(f"\n  Імпортовано {len(imported)} готелів.")
        except (FileNotFoundError, ValueError) as e:
            print(f"\n  Помилка: {e}")

    elif choice == "2":
        filepath = input("  Шлях до JSON файлу: ").strip()
        try:
            from booking_service.file_handler import import_json
            data = import_json(filepath)
            HOTELS.clear()
            HOTELS.extend(data["hotels"])
            ROOMS.clear()
            ROOMS.extend(data["rooms"])
            BOOKINGS.clear()
            BOOKINGS.extend(data["bookings"])
            USERS.clear()
            USERS.extend(data["users"])
            print(f"\n  Імпортовано: {len(data['hotels'])} готелів, "
                  f"{len(data['rooms'])} кімнат, "
                  f"{len(data['bookings'])} бронювань.")
        except (FileNotFoundError, ValueError) as e:
            print(f"\n  Помилка: {e}")

    else:
        print("  Невідомий формат.")

    pause()
    
if __name__ == "__main__":
    main()