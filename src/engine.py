from datetime import date

# Імітація бази даних
hotels_db = [
    {
        "id": 1, 
        "name": "Kyiv Grand Hub", 
        "location": "Київ", 
        "price": 3200.0,
        "description": "Бізнес-готель у центрі столиці"
    },
    {
        "id": 2, 
        "name": "Lviv Old Town", 
        "location": "Львів", 
        "price": 2100.0,
        "description": "Автентичний готель біля Ратуші"
    },
    {
        "id": 3, 
        "name": "Bukovel Resort", 
        "location": "Поляниця", 
        "price": 4500.0,
        "description": "Гірськолижний курорт преміум-класу"
    },
    {
        "id": 4, 
        "name": "Odesa Black Sea", 
        "location": "Одеса", 
        "price": 2800.0,
        "description": "Готель на першій лінії моря"
    },
    {
        "id": 5, 
        "name": "Kharkiv Modern", 
        "location": "Харків", 
        "price": 1900.0,
        "description": "Сучасні апартаменти в діловому районі"
    },
    {
        "id": 6, 
        "name": "Ivano-Frankivsk Inn", 
        "location": "Івано-Франківськ", 
        "price": 1400.0,
        "description": "Затишний готель у затишному місті"
    }
]

def get_filtered_hotels(city: str = None, max_price: float = None):
    """Фільтрація списку готелів (Етап 1: Пошуковий рушій)"""
    results = hotels_db
    if city:
        results = [h for h in results if city.lower() in h['location'].lower()]
    if max_price:
        results = [h for h in results if h['price'] <= max_price]
    return results

def validate_dates(check_in: date, check_out: date):
    """Складна валідація дат (Етап 1: Бізнес-логіка)"""
    today = date.today()
    
    if check_in < today:
        return False, "Помилка: Дата заїзду не може бути в минулому."
    
    if check_out <= check_in:
        return False, "Помилка: Дата виїзду має бути пізніше заїзду."
    
    duration = (check_out - check_in).days
    if duration > 30:
        return False, "Помилка: Максимальний термін бронювання — 30 днів."
        
    return True, f"Тривалість: {duration} ночей."

def calculate_price(price_per_night: float, check_in: date, check_out: date) -> float:
    """Розрахунок вартості (Етап 1: Фінансова логіка)"""
    nights = (check_out - check_in).days
    return nights * price_per_night