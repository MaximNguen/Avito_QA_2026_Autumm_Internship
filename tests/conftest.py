"""Pytest-фикстуры: пользователи, авторизованные клиенты, тестовые данные."""

from typing import Generator

import pytest
import allure

from src.clients.auth_client import AuthClient
from src.clients.item_client import ItemClient
from src.clients.statistic_client import StatisticClient
from src.models.auth import AutorizeResponse, RegisterResponse, RegisteredUser, CreatedItem
from src.utils.helpers import extract_item_id_from_response
from src.utils.payloads import (
    build_autorize_payload,
    build_item_payload,
    build_register_payload,
)


@pytest.fixture
def auth_client() -> AuthClient:
    """Клиент публичных ручек."""
    return AuthClient()


@pytest.fixture
def registered_user(auth_client: AuthClient) -> RegisteredUser:
    """Регистрация уникального пользователя."""
    with allure.step("Регистрация уникального пользователя"):
        payload = build_register_payload()
        response = auth_client.register(payload)
        assert response.status_code == 201, (
            f"Не удалось зарегистрировать пользователя: {response.status_code} " f"{response.text}"
        )
        user = RegisterResponse.model_validate(response.json())
        return RegisteredUser(id=user.id, username=user.username, password=payload["password"])


@pytest.fixture
def access_token(auth_client: AuthClient, registered_user: RegisteredUser) -> str:
    """Bearer-токен зарегистрированного пользователя."""
    with allure.step("Получение Bearer-токена"):
        response = auth_client.autorize(
            build_autorize_payload(registered_user.username, registered_user.password)
        )
        assert (
            response.status_code == 200
        ), f"Не удалось авторизоваться: {response.status_code} {response.text}"
        return AutorizeResponse.model_validate(response.json()).accessToken


@pytest.fixture
def item_client(access_token: str) -> ItemClient:
    """Авторизованный клиент ручек объявлений."""
    client = ItemClient()
    client.set_bearer_token(access_token)
    return client


@pytest.fixture
def statistic_client(access_token: str) -> StatisticClient:
    """Авторизованный клиент ручек статистики."""
    client = StatisticClient()
    client.set_bearer_token(access_token)
    return client


@pytest.fixture
def created_item(
    item_client: ItemClient, registered_user: RegisteredUser
) -> Generator[CreatedItem, None, None]:
    """Создание объявления перед тестом и его удаление после.

    Избавляет тесты от повторяющейся логики извлечения UUID и удаления.
    """
    with allure.step("Создание объявления для теста c удалением после окончания теста"):
        payload = build_item_payload(seller_id=registered_user.id)
        response = item_client.create_item(payload)
        assert (
            response.status_code == 200
        ), f"Не удалось создать объявление: {response.status_code} {response.text}"
        item_id = extract_item_id_from_response(response)
        assert item_id, f"В ответе на создание нет UUID объявления: {response.text}"

        yield CreatedItem(id=item_id, payload=payload)

        try:
            item_client.delete_item(item_id)
        except Exception:
            pass


@pytest.fixture
def second_item_client(auth_client: AuthClient) -> ItemClient:
    """Авторизованный клиент второго (другого) пользователя.

    Нужен для проверок изоляции данных между продавцами.
    """
    with allure.step("Регистрация второго пользователя и получение авторизованного клиента"):
        payload = build_register_payload()
        register_response = auth_client.register(payload)
        assert register_response.status_code == 201, (
            f"Не удалось зарегистрировать второго пользователя: "
            f"{register_response.status_code} {register_response.text}"
        )
        token_response = auth_client.autorize(
            build_autorize_payload(payload["username"], payload["password"])
        )
        assert token_response.status_code == 200, (
            f"Не удалось авторизовать второго пользователя: "
            f"{token_response.status_code} {token_response.text}"
        )
        token = AutorizeResponse.model_validate(token_response.json()).accessToken
        client = ItemClient()
        client.set_bearer_token(token)
        return client
