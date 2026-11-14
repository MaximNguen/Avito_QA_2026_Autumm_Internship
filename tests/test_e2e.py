"""Сквозной E2E-сценарий:
регистрация → авторизация → создание объявления → получение объявления
и статистики → удаление."""

import allure

from src.clients.auth_client import AuthClient
from src.clients.item_client import ItemClient
from src.clients.statistic_client import StatisticClient
from src.models.auth import AutorizeResponse, RegisterResponse
from src.models.item import Statistics
from src.utils.helpers import (
    extract_item_id_from_response,
    find_item_by_id,
    parse_items,
)
from src.utils.payloads import (
    build_autorize_payload,
    build_item_payload,
    build_register_payload,
)


@allure.feature("E2E")
@allure.story("Полный жизненный цикл объявления")
class TestItemLifecycleE2E:
    """Сквозной сценарий от регистрации до удаления объявления."""

    @allure.title("Регистрация → авторизация → создание → чтение → статистика → удаление")
    def test_item_full_lifecycle(self) -> None:
        auth_client = AuthClient()
        item_client = ItemClient()
        statistic_client = StatisticClient()

        with allure.step("1. Регистрация нового пользователя"):
            register_payload = build_register_payload()
            register_response = auth_client.register(register_payload)
            assert register_response.status_code == 201, (
                f"Регистрация не удалась: {register_response.status_code} "
                f"{register_response.text}"
            )
            user = RegisterResponse.model_validate(register_response.json())
            assert user.username == register_payload["username"]

        with allure.step("2. Авторизация и получение bearer-токена"):
            autorize_response = auth_client.autorize(
                build_autorize_payload(user.username, register_payload["password"])
            )
            assert autorize_response.status_code == 200, (
                f"Авторизация не удалась: {autorize_response.status_code} "
                f"{autorize_response.text}"
            )
            token = AutorizeResponse.model_validate(autorize_response.json())
            assert token.tokenType == "Bearer"
            item_client.set_bearer_token(token.accessToken)
            statistic_client.set_bearer_token(token.accessToken)

        with allure.step("3. Создание объявления"):
            item_payload = build_item_payload(seller_id=user.id)
            create_response = item_client.create_item(item_payload)
            assert create_response.status_code == 200, (
                f"Создание не удалось: {create_response.status_code} " f"{create_response.text}"
            )
            item_id = extract_item_id_from_response(create_response)
            assert item_id, f"В ответе нет UUID объявления: {create_response.text}"

        try:
            with allure.step("4. Получение объявления по id"):
                get_response = item_client.get_item_by_id(item_id)
                assert get_response.status_code == 200
                item = find_item_by_id(parse_items(get_response), item_id)
                assert item is not None
                assert item.sellerId == user.id
                assert item.name == item_payload["name"]
                assert item.price == item_payload["price"]

            with allure.step("5. Получение объявления в списке объявлений продавца"):
                seller_response = item_client.get_items_by_seller(user.id)
                assert seller_response.status_code == 200
                assert find_item_by_id(
                    parse_items(seller_response), item_id
                ), "Объявления нет в списке объявлений продавца"

            with allure.step("6. Получение статистики объявления (v1 и v2)"):
                for get_statistic in (
                    statistic_client.get_statistic_v1,
                    statistic_client.get_statistic_v2,
                ):
                    statistic_response = get_statistic(item_id)
                    assert statistic_response.status_code == 200
                    body = statistic_response.json()
                    assert isinstance(body, list) and len(body) == 1
                    statistic = Statistics.model_validate(body[0])
                    assert statistic.model_dump() == item_payload["statistics"]

            with allure.step("7. Удаление объявления"):
                delete_response = item_client.delete_item(item_id)
                assert delete_response.status_code == 200, (
                    f"Удаление не удалось: {delete_response.status_code} " f"{delete_response.text}"
                )

            with allure.step("8. Объявление недоступно после удаления"):
                get_deleted_response = item_client.get_item_by_id(item_id)
                assert get_deleted_response.status_code == 404
        finally:
            item_client.delete_item(item_id)
