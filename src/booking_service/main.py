from datetime import datetime

from booking_service.core.exceptions import BookingServiceError

# Коректний імпорт для структури пакета
from booking_service.engine import calculate_price, get_filtered_hotels, validate_dates


def get_date_input(prompt):
    while True:
        date_str = input(prompt)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Помилка: Формат має бути РРРР-ММ-ДД.")

def main():
    print("-" * 40)
    print("🏨 СИСТЕМА ОНЛАЙН-БРОНЮВАННЯ")
    print("-" * 40)

    while True:
        print("\n1. Пошук | 2. Бронювання | 0. Вихід")
        choice = input("Ваш вибір: ")

        if choice == "1":
            city = input("Місто: ")
            hotels = get_filtered_hotels(city)
            for h in hotels:
                print(f"ID: {h['id']} | {h['name']} | {h['price']} грн")

        elif choice == "2":
            try:
                h_id = int(input("Введіть ID готелю: "))
                hotel = next((h for h in get_filtered_hotels() if h['id'] == h_id), None)
                
                if not hotel:
                    print("❌ Помилка: Готель не знайдено.")
                    continue

                check_in = get_date_input("Дата заїзду: ")
                check_out = get_date_input("Дата виїзду: ")
                
                # Викликаємо логіку (вона сама викине Exception якщо щось не так)
                nights = validate_dates(check_in, check_out)
                total = calculate_price(hotel['price'], check_in, check_out)
                
                print(f"\n✅ Успішно! Ночей: {nights}")
                print(f"До сплати: {total} грн.")

            except BookingServiceError as e:
                # Відловлюємо наші специфічні помилки
                print(f"⚠️ Увага: {e.message}")
            except ValueError:
                print("❌ Помилка: Вводьте коректні числа.")

        elif choice == "0":
            break

if __name__ == "__main__":
    main()