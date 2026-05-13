"""Тести для бізнес-логіки системи бронювання — utils.py."""

from datetime import date, timedelta

import pytest

from booking_service.models import Booking, Room
from booking_service.repository import (
    calculate_total_price,
    filter_hotels_by_city,
    filter_rooms_by_price,
    is_dates_valid,
    is_room_available,
)


class TestCalculateTotalPrice:
    """Тести для функції calculate_total_price()."""

    def test_correct_price_for_3_nights(self, sample_room, future_dates):
        """Розраховує коректну вартість для 3 ночей."""
        check_in, check_out = future_dates
        # future_dates: завтра — через 4 дні = 3 ночі
        result = calculate_total_price(sample_room, check_in, check_out)
        assert result == 3000.0

    def test_correct_price_for_1_night(self, sample_room):
        """Розраховує коректну вартість для 1 ночі."""
        today = date.today()
        check_in = today + timedelta(days=1)
        check_out = today + timedelta(days=2)
        result = calculate_total_price(sample_room, check_in, check_out)
        assert result == 1000.0

    def test_price_multiplied_by_nights(self, sample_room):
        """Ціна = price_per_night * кількість ночей."""
        today = date.today()
        check_in = today + timedelta(days=1)
        check_out = today + timedelta(days=6)
        result = calculate_total_price(sample_room, check_in, check_out)
        assert result == sample_room.price_per_night * 5

    def test_raises_if_checkout_before_checkin(self, sample_room):
        """Викидає ValueError якщо виїзд до заїзду."""
        today = date.today()
        check_in = today + timedelta(days=3)
        check_out = today + timedelta(days=1)
        with pytest.raises(ValueError):
            calculate_total_price(sample_room, check_in, check_out)

    def test_raises_if_same_dates(self, sample_room):
        """Викидає ValueError якщо дати однакові."""
        today = date.today()
        check_in = today + timedelta(days=1)
        with pytest.raises(ValueError):
            calculate_total_price(sample_room, check_in, check_in)

    def test_result_is_rounded_to_2_decimals(self):
        """Результат округлений до 2 знаків після коми."""
        room = Room(1, 1, "101", "single", 333.33)
        today = date.today()
        check_in = today + timedelta(days=1)
        check_out = today + timedelta(days=4)
        result = calculate_total_price(room, check_in, check_out)
        # 333.33 * 3 = 999.99
        assert result == 999.99


class TestIsDatesValid:
    """Тести для функції is_dates_valid()."""

    def test_valid_future_dates(self, future_dates):
        """Майбутні коректні дати повертають True."""
        check_in, check_out = future_dates
        assert is_dates_valid(check_in, check_out) is True

    def test_invalid_past_checkin(self):
        """Дата заїзду в минулому повертає False."""
        yesterday = date.today() - timedelta(days=1)
        check_out = date.today() + timedelta(days=2)
        assert is_dates_valid(yesterday, check_out) is False

    def test_invalid_checkout_before_checkin(self):
        """Виїзд до заїзду повертає False."""
        today = date.today()
        check_in = today + timedelta(days=3)
        check_out = today + timedelta(days=1)
        assert is_dates_valid(check_in, check_out) is False

    def test_invalid_same_dates(self):
        """Однакові дати заїзду та виїзду повертають False."""
        tomorrow = date.today() + timedelta(days=1)
        assert is_dates_valid(tomorrow, tomorrow) is False

    def test_valid_today_checkin(self):
        """Заїзд сьогодні є коректним."""
        today = date.today()
        check_out = today + timedelta(days=2)
        assert is_dates_valid(today, check_out) is True


class TestIsRoomAvailable:
    """Тести для функції is_room_available()."""

    def test_available_when_no_bookings(self, future_dates):
        """Кімната вільна якщо немає жодних бронювань."""
        check_in, check_out = future_dates
        assert is_room_available(1, check_in, check_out, []) is True

    def test_unavailable_when_dates_overlap(self, future_dates):
        """Кімната зайнята якщо дати перетинаються."""
        check_in, check_out = future_dates
        existing = Booking(
            id=1, user_id=1, room_id=1,
            check_in=check_in,
            check_out=check_out,
            total_price=3000.0,
            status="confirmed",
        )
        assert is_room_available(1, check_in, check_out, [existing]) is False

    def test_available_after_existing_booking(self):
        """Кімната вільна якщо новий заїзд після виїзду існуючого."""
        today = date.today()
        existing = Booking(
            id=1, user_id=1, room_id=1,
            check_in=today + timedelta(days=1),
            check_out=today + timedelta(days=4),
            total_price=3000.0,
            status="confirmed",
        )
        # Новий заїзд після виїзду існуючого
        new_check_in = today + timedelta(days=4)
        new_check_out = today + timedelta(days=7)
        assert is_room_available(1, new_check_in, new_check_out, [existing]) is True

    def test_available_before_existing_booking(self):
        """Кімната вільна якщо виїзд до заїзду існуючого."""
        today = date.today()
        existing = Booking(
            id=1, user_id=1, room_id=1,
            check_in=today + timedelta(days=5),
            check_out=today + timedelta(days=8),
            total_price=3000.0,
            status="confirmed",
        )
        # Виїзд до заїзду існуючого бронювання
        new_check_in = today + timedelta(days=1)
        new_check_out = today + timedelta(days=5)
        assert is_room_available(1, new_check_in, new_check_out, [existing]) is True

    def test_available_if_booking_is_cancelled(self, future_dates):
        """Скасоване бронювання не блокує кімнату."""
        check_in, check_out = future_dates
        cancelled = Booking(
            id=1, user_id=1, room_id=1,
            check_in=check_in,
            check_out=check_out,
            total_price=3000.0,
            status="cancelled",
        )
        assert is_room_available(1, check_in, check_out, [cancelled]) is True

    def test_available_for_different_room(self, future_dates):
        """Бронювання іншої кімнати не впливає на доступність."""
        check_in, check_out = future_dates
        other_room_booking = Booking(
            id=1, user_id=1, room_id=2,
            check_in=check_in,
            check_out=check_out,
            total_price=3000.0,
            status="confirmed",
        )
        # Перевіряємо кімнату 1 — бронювання на кімнату 2 не заважає
        assert is_room_available(1, check_in, check_out, [other_room_booking]) is True

    def test_unavailable_partial_overlap_start(self):
        """Кімната зайнята якщо новий заїзд в середині існуючого."""
        today = date.today()
        existing = Booking(
            id=1, user_id=1, room_id=1,
            check_in=today + timedelta(days=1),
            check_out=today + timedelta(days=6),
            total_price=5000.0,
            status="confirmed",
        )
        # Новий заїзд всередині існуючого бронювання
        new_check_in = today + timedelta(days=3)
        new_check_out = today + timedelta(days=8)
        assert is_room_available(1, new_check_in, new_check_out, [existing]) is False


class TestFilterHotelsByCity:
    """Тести для функції filter_hotels_by_city()."""

    def test_filters_by_city(self, sample_hotel):
        """Повертає готелі з вказаного міста."""
        result = filter_hotels_by_city([sample_hotel], "Київ")
        assert len(result) == 1
        assert result[0] == sample_hotel

    def test_case_insensitive(self, sample_hotel):
        """Фільтрація не залежить від регістру."""
        assert filter_hotels_by_city([sample_hotel], "київ") == [sample_hotel]
        assert filter_hotels_by_city([sample_hotel], "КИЇВ") == [sample_hotel]
        assert filter_hotels_by_city([sample_hotel], "Київ") == [sample_hotel]

    def test_returns_empty_for_unknown_city(self, sample_hotel):
        """Повертає порожній список якщо місто не знайдено."""
        result = filter_hotels_by_city([sample_hotel], "Одеса")
        assert result == []

    def test_returns_empty_for_empty_list(self):
        """Повертає порожній список якщо список готелів порожній."""
        result = filter_hotels_by_city([], "Київ")
        assert result == []

    def test_filters_multiple_hotels(self):
        """Повертає кілька готелів одного міста."""
        from booking_service.models import Hotel
        hotels = [
            Hotel(1, "Hotel A", "Київ", "вул. 1", 3),
            Hotel(2, "Hotel B", "Одеса", "вул. 2", 4),
            Hotel(3, "Hotel C", "Київ", "вул. 3", 5),
        ]
        result = filter_hotels_by_city(hotels, "Київ")
        assert len(result) == 2


class TestFilterRoomsByPrice:
    """Тести для функції filter_rooms_by_price()."""

    def test_filters_by_max_price(self, sample_room):
        """Повертає кімнати що не перевищують ціну."""
        result = filter_rooms_by_price([sample_room], max_price=1500.0)
        assert sample_room in result

    def test_excludes_expensive_rooms(self, sample_room):
        """Виключає кімнати дорожчі за ліміт."""
        result = filter_rooms_by_price([sample_room], max_price=500.0)
        assert result == []

    def test_includes_exact_price(self, sample_room):
        """Включає кімнату з ціною рівно на межі."""
        # sample_room.price_per_night == 1000.0
        result = filter_rooms_by_price([sample_room], max_price=1000.0)
        assert sample_room in result

    def test_returns_empty_for_empty_list(self):
        """Повертає порожній список якщо список кімнат порожній."""
        result = filter_rooms_by_price([], max_price=5000.0)
        assert result == []

    def test_filters_multiple_rooms(self):
        """Коректно фільтрує список з кількох кімнат."""
        rooms = [
            Room(1, 1, "101", "single", 800.0),
            Room(2, 1, "202", "double", 1500.0),
            Room(3, 1, "301", "suite", 4000.0),
        ]
        result = filter_rooms_by_price(rooms, max_price=1500.0)
        assert len(result) == 2
        assert rooms[2] not in result