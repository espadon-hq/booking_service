import sys
import os

# Додаємо папку src до шляхів, щоб імпорти всередині вашого коду працювали
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from booking_service.main import app

# Vercel тепер побачить цей файл і імпортований об'єкт 'app'