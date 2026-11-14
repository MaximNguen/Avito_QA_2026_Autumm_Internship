from typing import Any, Dict

import requests
import allure

from src.clients.base_client import BaseClient


class AuthClient(BaseClient):
    """Публичные ручки: регистрация и авторизация."""

    def register(self, payload: Dict[str, Any]) -> requests.Response:
        """POST /api/1/register — зарегистрировать пользователя."""
        with allure.step("Регистрация нового пользователя"):
            return self.request("POST", "/api/1/register", json=payload)

    def autorize(self, payload: Dict[str, Any]) -> requests.Response:
        """POST /api/1/autorize — получить bearer-токен."""
        with allure.step("Авторизация пользователя"):
            return self.request("POST", "/api/1/autorize", json=payload)
