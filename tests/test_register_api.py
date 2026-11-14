"""Тесты ручки POST /api/1/register — регистрация пользователя."""

import allure
import pytest

from src.clients.auth_client import AuthClient
from src.models.auth import AuthErrorResponse, RegisterResponse
from src.utils.generators import Generator
from src.utils.payloads import build_register_payload


@allure.feature("Регистрация")
@allure.story("POST /api/1/register")
class TestRegisterAPI:
    """Позитивные, негативные и граничные проверки регистрации."""

    @allure.title("Успешная регистрация с уникальным username")
    def test_register_success(self, auth_client: AuthClient) -> None:
        payload = build_register_payload()
        response = auth_client.register(payload)

        assert (
            response.status_code == 201
        ), f"Ожидали 201, получили {response.status_code}. Ответ: {response.text}"
        user = RegisterResponse.model_validate(response.json())
        assert user.id > 0
        assert user.username == payload["username"]

    @allure.title("Повторная регистрация с тем же username отклоняется")
    def test_register_duplicate_username(self, auth_client: AuthClient) -> None:
        payload = build_register_payload()
        first_response = auth_client.register(payload)
        assert first_response.status_code == 201

        second_response = auth_client.register(payload)
        assert second_response.status_code == 409, (
            f"Ожидали 409, получили {second_response.status_code}. "
            f"Ответ: {second_response.text}"
        )
        AuthErrorResponse.model_validate(second_response.json())

    @allure.title("Регистрация с невалидными данными отклоняется")
    @pytest.mark.parametrize(
        "payload_overrides",
        [
            {"username": ""},
            {"password": ""},
            {"username": "", "password": ""},
        ],
        ids=["пустой username", "пустой password", "оба поля пустые"],
    )
    def test_register_invalid_data(
        self,
        auth_client: AuthClient,
        payload_overrides: dict,
    ) -> None:
        payload = {**build_register_payload(), **payload_overrides}
        response = auth_client.register(payload)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Регистрация без обязательного поля отклоняется")
    @pytest.mark.parametrize("missing_field", ["username", "password"])
    def test_register_missing_field(
        self,
        auth_client: AuthClient,
        missing_field: str,
    ) -> None:
        payload = build_register_payload()
        payload.pop(missing_field)
        response = auth_client.register(payload)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Регистрация с пустым телом запроса отклоняется")
    def test_register_empty_body(self, auth_client: AuthClient) -> None:
        response = auth_client.register({})
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.title("Граничные значения длины username (минимум 3 символа)")
    @pytest.mark.parametrize(
        "username_length, expected_code",
        [(2, 400), (3, 201)],
        ids=["2 символа — отказ", "3 символа — успех"],
    )
    def test_register_username_length_boundary(
        self,
        auth_client: AuthClient,
        username_length: int,
        expected_code: int,
    ) -> None:
        # username генерируем случайно: стенд общий, фиксированные значения
        # короткой длины могут быть уже заняты другими кандидатами
        username = Generator.generate_username()[-username_length:]
        payload = build_register_payload(username=username)
        response = auth_client.register(payload)
        assert response.status_code == expected_code, (
            f"Ожидали {expected_code}, получили {response.status_code}. " f"Ответ: {response.text}"
        )

    @allure.title("Граничные значения длины password (минимум 8 символов)")
    @pytest.mark.parametrize(
        "password_length, expected_code",
        [(7, 400), (8, 201)],
        ids=["7 символов — отказ", "8 символов — успех"],
    )
    def test_register_password_length_boundary(
        self,
        auth_client: AuthClient,
        password_length: int,
        expected_code: int,
    ) -> None:
        payload = build_register_payload(password="p" * password_length)
        response = auth_client.register(payload)
        assert response.status_code == expected_code, (
            f"Ожидали {expected_code}, получили {response.status_code}. " f"Ответ: {response.text}"
        )

    @allure.title("Зарегистрированный пользователь может авторизоваться")
    def test_registered_user_can_autorize(self, auth_client: AuthClient) -> None:
        payload = build_register_payload(
            username=Generator.generate_username(),
            password=Generator.generate_password(),
        )
        register_response = auth_client.register(payload)
        assert register_response.status_code == 201

        autorize_response = auth_client.autorize(payload)
        assert autorize_response.status_code == 200, (
            f"Пользователь не смог авторизоваться сразу после регистрации: "
            f"{autorize_response.status_code} {autorize_response.text}"
        )
