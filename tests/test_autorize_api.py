"""Тесты ручки POST /api/1/autorize — авторизация пользователя."""

import allure

from src.clients.auth_client import AuthClient
from src.models.auth import AutorizeResponse, RegisteredUser
from src.utils.generators import Generator
from src.utils.payloads import build_autorize_payload


@allure.feature("Авторизация")
@allure.story("POST /api/1/autorize")
class TestAutorizeAPI:
    """Позитивные и негативные проверки авторизации."""

    @allure.title("Успешная авторизация возвращает bearer-токен")
    def test_autorize_success(
        self,
        auth_client: AuthClient,
        registered_user: RegisteredUser,
    ) -> None:
        response = auth_client.autorize(
            build_autorize_payload(registered_user.username, registered_user.password)
        )

        assert (
            response.status_code == 200
        ), f"Ожидали 200, получили {response.status_code}. Ответ: {response.text}"
        token = AutorizeResponse.model_validate(response.json())
        assert token.tokenType == "Bearer"
        assert len(token.accessToken.split(".")) == 3

    @allure.title("Авторизация с неверным паролем отклоняется")
    def test_autorize_wrong_password(
        self,
        auth_client: AuthClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_autorize_payload(registered_user.username, Generator.generate_password())
        response = auth_client.autorize(payload)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Авторизация несуществующего пользователя отклоняется")
    def test_autorize_unknown_user(self, auth_client: AuthClient) -> None:
        payload = build_autorize_payload(
            Generator.generate_username(), Generator.generate_password()
        )
        response = auth_client.autorize(payload)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Авторизация с пустым телом запроса отклоняется")
    def test_autorize_empty_body(self, auth_client: AuthClient) -> None:
        response = auth_client.autorize({})
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Авторизация с паролем короче минимальной длины отклоняется")
    def test_autorize_short_password(
        self,
        auth_client: AuthClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_autorize_payload(registered_user.username, "short")
        response = auth_client.autorize(payload)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Авторизация с именем короче минимальной длины отклоняется")
    def test_autorize_short_username(
        self,
        auth_client: AuthClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_autorize_payload("aa", registered_user.password)
        response = auth_client.autorize(payload)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"
