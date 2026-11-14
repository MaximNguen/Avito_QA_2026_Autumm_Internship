import random
import uuid


class Generator:
    """Генератор уникальных тестовых данных (стенд общий)."""

    @staticmethod
    def generate_username() -> str:
        """Уникальный username (минимум 3 символа по валидации сервиса)."""
        return f"student_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_password() -> str:
        """Валидный пароль (минимум 8 символов по валидации сервиса)."""
        return f"Pass-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_item_name() -> str:
        """Уникальное название объявления."""
        return f"item-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_price() -> int:
        """Случайная положительная цена."""
        return random.randint(1, 1_000_000)

    @staticmethod
    def generate_statistics() -> dict:
        """Случайная неотрицательная статистика."""
        return {
            "likes": random.randint(0, 1000),
            "viewCount": random.randint(0, 10000),
            "contacts": random.randint(0, 500),
        }

    @staticmethod
    def generate_non_existent_uuid() -> str:
        """UUID, которого нет на стенде (вероятность коллизии ~0)."""
        return str(uuid.uuid4())
