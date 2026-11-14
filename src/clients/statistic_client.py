import allure
import requests

from src.clients.base_client import BaseClient


class StatisticClient(BaseClient):
    """Защищённые ручки статистики (требуется bearer-токен)."""

    def get_statistic_v1(self, item_id: str) -> requests.Response:
        """GET /api/1/statistic/{id} — статистика объявления, версия 1."""
        with allure.step(f"Получение статистики v1 для объявления id: {item_id}"):
            return self.request("GET", f"/api/1/statistic/{item_id}")

    def get_statistic_v2(self, item_id: str) -> requests.Response:
        """GET /api/2/statistic/{id} — статистика объявления, версия 2."""
        with allure.step(f"Получение статистики v2 для объявления id: {item_id}"):
            return self.request("GET", f"/api/2/statistic/{item_id}")
