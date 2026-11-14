import time
from typing import Any, Dict, Optional

import requests
import allure

from src.config import BASE_URL, TIMEOUT_SECONDS


class BaseClient:
    """Базовый HTTP-клиент: сессия, заголовки, bearer-токен."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> None:
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds or TIMEOUT_SECONDS
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )

    def set_bearer_token(self, token: str) -> None:
        """Установить заголовок Authorization: Bearer <token>."""
        with allure.step("Установка заголовка Authorization"):
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_bearer_token(self) -> None:
        """Убрать заголовок Authorization (сценарии без токена)."""
        with allure.step("Очистка заголовка Authorization"):
            self.session.headers.pop("Authorization", None)

    def request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Отправка запроса и получение ответа.

        Стенд общий и иногда разрывает соединение — делаем несколько попыток
        при сетевых сбоях, чтобы тесты не падали по инфраструктурным причинам.
        """
        url = f"{self.base_url}{path}"
        last_error: Optional[requests.ConnectionError] = None
        with allure.step("Отправка запроса"):
            for attempt in range(3):
                try:
                    return self.session.request(
                        method=method,
                        url=url,
                        json=json,
                        timeout=self.timeout_seconds,
                    )
                except requests.ConnectionError as error:
                    last_error = error
                    time.sleep(1 + attempt)
            raise last_error
