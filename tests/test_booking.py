from datetime import date, timedelta

from engine import calculate_price, validate_dates


# Тест розрахунку ціни
def test_calculate_price():
    check_in = date.today()
    check_out = check_in + timedelta(days=3)  # 3 ночі
    price_per_night = 1000.0
    
    total = calculate_price(price_per_night, check_in, check_out)
    
    assert total == 3000.0  # Очікуємо 3000
    assert isinstance(total, float)

# Тест правильної валідації дат
def test_validate_dates_correct():
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    
    is_valid, message = validate_dates(check_in, check_out)
    
    assert is_valid is True
    assert "Тривалість" in message

# Тест помилки: дата в минулому
def test_validate_dates_past():
    check_in = date.today() - timedelta(days=5)
    check_out = date.today() + timedelta(days=2)
    
    is_valid, message = validate_dates(check_in, check_out)
    
    assert is_valid is False
    assert "минулому" in message.lower()

# Тест помилки: виїзд раніше заїзду
def test_validate_dates_invalid_range():
    check_in = date.today() + timedelta(days=5)
    check_out = date.today() + timedelta(days=2)
    
    is_valid, message = validate_dates(check_in, check_out)
    
    assert is_valid is False
    assert "пізніше" in message.lower()