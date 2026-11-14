from typing import Any, Dict, Union

import requests
import allure

from src.clients.base_client import BaseClient


class ItemClient(BaseClient):
    """Защищённые ручки объявлений (требуется bearer-токен)."""

    def create_item(self, payload: Dict[str, Any]) -> requests.Response:
        """POST /api/1/item — создать объявление."""
        with allure.step("Создание нового объявления"):
            return self.request("POST", "/api/1/item", json=payload)

    def get_item_by_id(self, item_id: str) -> requests.Response:
        """GET /api/1/item/{id} — получить объявление по идентификатору."""
        with allure.step(f"Получение объявления по id: {item_id}"):
            return self.request("GET", f"/api/1/item/{item_id}")

    def get_items_by_seller(self, seller_id: Union[int, str]) -> requests.Response:
        """GET /api/1/{sellerID}/item — получить все объявления продавца."""
        with allure.step(f"Получение всех объявлений продавца: {seller_id}"):
            return self.request("GET", f"/api/1/{seller_id}/item")

    def delete_item(self, item_id: str) -> requests.Response:
        """DELETE /api/2/item/{id} — удалить объявление по идентификатору."""
        with allure.step(f"Удаление объявления по id: {item_id}"):
            return self.request("DELETE", f"/api/2/item/{item_id}")
