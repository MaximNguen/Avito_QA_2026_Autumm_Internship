"""Вспомогательные функции, переиспользуемые в тестах."""

import re
from typing import TYPE_CHECKING, List, Optional

import requests
import allure

from src.models.item import Item

if TYPE_CHECKING:
    from src.clients.item_client import ItemClient

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-" r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def extract_item_id(status: str) -> Optional[str]:
    """Извлечь UUID объявления из строки status ответа POST /api/1/item.

    Пример status: 'Сохранили объявление - 550e8400-e29b-41d4-a716-446655440000'.
    """
    with allure.step(f"Извлечение UUID объявления из строки: {status}"):
        match = UUID_PATTERN.search(status or "")
        return match.group(0) if match else None


def extract_item_id_from_response(response: requests.Response) -> Optional[str]:
    """Извлечь UUID объявления из тела ответа на создание."""
    with allure.step(f"Извлечение UUID объявления из ответа: {response.text}"):
        try:
            body = response.json()
        except ValueError:
            return None
        if not isinstance(body, dict):
            return None
        return extract_item_id(str(body.get("status", "")))


def parse_items(response: requests.Response) -> List[Item]:
    """Распарсить тело ответа GET-ручек объявлений в список моделей."""
    with allure.step(f"Распарсить тело ответа: {response.text}"):
        body = response.json()
        assert isinstance(body, list), f"Ожидали массив объявлений, получили: {body}"
        return [Item.model_validate(item) for item in body]


def find_item_by_id(items: List[Item], item_id: str) -> Optional[Item]:
    """Найти объявление по id в списке, возвращённом GET-ручками."""
    with allure.step(f"Поиск объявления по id: {item_id} в списке из {len(items)} элементов"):
        for item in items:
            if item.id == item_id:
                return item
        return None


def cleanup_item_if_created(item_client: "ItemClient", response: requests.Response) -> None:
    """Удалить объявление, если оно всё же было создано.

    Используется в негативных тестах: при баге сервис создаёт объявление,
    и его нужно убрать, чтобы вернуть окружение в исходное состояние.
    """
    with allure.step("Очистка объявления, если оно было создано"):
        if response.status_code == 200:
            item_id = extract_item_id_from_response(response)
            if item_id:
                item_client.delete_item(item_id)
