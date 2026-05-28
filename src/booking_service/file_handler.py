"""Робота з файлами — JSON експорт/імпорт."""
import json
import os
from datetime import date


def export_json(data: list, filepath: str) -> None:
    """Експортує список об'єктів у JSON файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None

    def serialize(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return obj.__dict__ if hasattr(obj, '__dict__') else str(obj)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=serialize, indent=2, ensure_ascii=False)


def import_json(filepath: str) -> list:
    """Імпортує список об'єктів з JSON файлу."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не знайдено: {filepath}")
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)
