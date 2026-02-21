import os
import sys
from datetime import datetime

# Додаємо шлях до src для імпорту engine та models
sys.path.append(os.path.dirname(__file__))
from engine import calculate_price, get_filtered_hotels, validate_dates


def get_date_input(prompt):
    """Безпечне введення дати у форматі РРРР-ММ-ДД"""
    while True:
        date_str = input(prompt)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Помилка: Формат має бути РРРР-ММ-ДД.")

def main():
    print("-" * 40)
    print("СИСТЕМА ОНЛАЙН-БРОНЮВАННЯ ГОТЕЛІВ")
    print("-" * 40)

    while True:
        print("\nМЕНЮ:")
        print("1. Пошук готелів")
        print("2. Бронювання")
        print("0. Вихід")
        
        choice = input("\nВаш вибір: ")

        if choice == "1":
            city = input("Місто (Enter для всіх): ")
            price_limit = input("Макс. ціна (Enter для пропуску): ")
            price_limit = float(price_limit) if price_limit else None
            
            # Виклик функції пошуку з engine.py
            hotels = get_filtered_hotels(city, price_limit)
            print(f"\nЗнайдено: {len(hotels)}")
            for h in hotels:
                print(f"ID: {h['id']} | {h['name']} | {h['location']} | {h['price']} грн")

        elif choice == "2":
            try:
                h_id = int(input("Введіть ID готелю: "))
                hotel = next((h for h in get_filtered_hotels() if h['id'] == h_id), None)
                
                if not hotel:
                    print("Помилка: Готель не знайдено.")
                    continue

                check_in = get_date_input("Дата заїзду (РРРР-ММ-ДД): ")
                check_out = get_date_input("Дата виїзду (РРРР-ММ-ДД): ")
                
                # Валідація та розрахунок вартості
                is_valid, message = validate_dates(check_in, check_out)
                
                if is_valid:
                    total = calculate_price(hotel['price'], check_in, check_out)
                    print(f"\nСтатус: {message}")
                    print(f"До сплати: {total} грн.")
                    print(f"Готель '{hotel['name']}' заброньовано успішно.")
                else:
                    print(f"\n{message}")
            except ValueError:
                print("Помилка: Вводьте лише числа для ID.")

        elif choice == "0":
            break

if __name__ == "__main__":
    main()