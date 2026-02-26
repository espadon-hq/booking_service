class BookingServiceError(Exception):
    """Базовий клас для всіх виключень у нашому сервісі.
    Від нього будуть успадковуватися всі інші помилки.
    """
    def __init__(self, message="Виникла помилка у сервісі бронювання"):
        self.message = message
        super().__init__(self.message)


class ValidationError(BookingServiceError):
    """Викликається, якщо дані не пройшли перевірку (наприклад, некоректний email)"""
    pass


class RoomNotFoundError(BookingServiceError):
    """Викликається, якщо кімнати з таким ID не існує"""
    pass


class RoomAlreadyBookedError(BookingServiceError):
    """Викликається, якщо користувач намагається забронювати вже зайняту кімнату"""
    pass


class InvalidBookingDatesError(BookingServiceError):
    """Викликається, якщо дата виїзду раніше за дату заїзду"""
    pass