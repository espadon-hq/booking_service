# Booking Service
Веб-застосунок для онлайн-бронювання готелів з REST API та веб-інтерфейсом.
## Що цеBooking Service:
- переглядати готелі та кімнати
- перевіряти доступність кімнат за датами
- бронювати кімнати онлайн
- керувати бронюваннями
Застосунок має два інтерфейси — веб-сторінки для браузера та REST API для зовнішніх клієнтів.
---
## Стек технологій
| Технологія | Роль |
|------------|------|
| Python 3.14 | Мова програмування |
| FastAPI | Веб-фреймворк |
| Uvicorn | ASGI веб-сервер |
| SQLAlchemy | ORM — робота з БД через Python об'єкти |
| PostgreSQL | База даних |
| Docker | Запуск PostgreSQL в контейнері |
| Pydantic v2 | Валідація даних та конфігурація |
| Jinja2 | HTML шаблони |
| pytest | Тестування |
---

## Структура проекту

```
booking_service/
├── src/booking_service/
│   ├── database.py       — конфігурація, підключення до PostgreSQL, ORM моделі
│   ├── models.py         — dataclass моделі
│   ├── schemas.py        — Pydantic схеми для API
│   ├── repository.py     — CRUD операції та бізнес-логіка
│   ├── main.py           — точка входу FastAPI
│   └── routers/
│       ├── hotels.py     — REST API /hotels
│       ├── rooms.py      — REST API /hotels/{id}/rooms
│       ├── users.py      — REST API /users
│       ├── bookings.py   — REST API /bookings
│       └── web.py        — веб-інтерфейс (HTML сторінки)
│   └── templates/
│       ├── base.html         — базовий шаблон (navbar, стилі)
│       ├── hotels.html       — список готелів
│       ├── hotel_detail.html — готель, кімнати, форма бронювання
│       └── bookings.html     — список бронювань
├── tests/
│   ├── conftest.py           — спільні фікстури
│   ├── test_models.py        — тести dataclass моделей
│   ├── test_utils.py         — тести бізнес-логіки
│   ├── test_repository.py    — тести CRUD операцій
│   └── test_api.py           — тести REST API
├── docker-compose.yml        — PostgreSQL контейнер
├── .env                      — змінні середовища
└── README.md
```
---

## Запуск


```bash
 1. Запустити PostgreSQL
docker-compose up -d
 

 2. Створити таблиці
python -c "from booking\_service.database import init\_db; init\_db()"


 3. Запустити сервер

uvicorn booking\_service.main:app --reload

 або
python src/booking\_service/main.py

```
Веб-інтерфейс: http://localhost:8000

Swagger API docs: http://localhost:8000/docs
---


## Тести

 ```bash
pytest -v
```
103 тести: моделі, бізнес-логіка, репозиторій, API.
---

## REST API
| Метод | Ендпоінт | Опис |
|-------|----------|------|
| GET | /hotels/ | Список готелів |
| POST | /hotels/ | Створити готель |
| GET | /hotels/{id} | Готель за id |
| PATCH | /hotels/{id} | Оновити готель |
| DELETE | /hotels/{id} | Видалити готель |
| GET | /hotels/{id}/rooms/ | Кімнати готелю |
| POST | /hotels/{id}/rooms/ | Створити кімнату |
| GET | /hotels/{id}/rooms/available | Доступні кімнати за датами |
| GET | /users/ | Список користувачів |
| POST | /users/ | Створити користувача |
| GET | /users/{id} | Користувач за id |
| GET | /users/{id}/bookings | Бронювання користувача |
| GET | /bookings/ | Список бронювань |
| POST | /bookings/ | Створити бронювання |
| GET | /bookings/{id} | Бронювання за id |
| POST | /bookings/{id}/cancel | Скасувати бронювання |
 

