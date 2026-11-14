"""Тесты ручек объявлений: POST /api/1/item, GET /api/1/item/{id},
GET /api/1/{sellerID}/item, DELETE /api/2/item/{id}."""

import allure
import pytest

from src.clients.item_client import ItemClient
from src.utils.generators import Generator
from src.utils.helpers import (
    cleanup_item_if_created,
    extract_item_id_from_response,
    find_item_by_id,
    parse_items,
)
from src.utils.payloads import build_item_payload
from src.models.auth import CreatedItem, RegisteredUser


@allure.feature("Объявления")
class TestItemAPI:
    """Позитивные, негативные и граничные проверки CRUD объявлений."""

    # ---------- POST /api/1/item ----------

    @allure.story("POST /api/1/item")
    @allure.title("Успешное создание объявления")
    def test_create_item_success(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        response = item_client.create_item(payload)

        try:
            assert response.status_code == 200, (
                f"Ожидали 200, получили {response.status_code}. " f"Ответ: {response.text}"
            )
            item_id = extract_item_id_from_response(response)
            assert item_id, f"В ответе нет UUID объявления: {response.text}"

            get_response = item_client.get_item_by_id(item_id)
            assert get_response.status_code == 200
            item = find_item_by_id(parse_items(get_response), item_id)
            assert item is not None, "Созданное объявление не найдено по id"
            assert item.sellerId == payload["sellerID"]
            assert item.name == payload["name"]
            assert item.price == payload["price"]
        finally:
            cleanup_item_if_created(item_client, response)

    @allure.story("POST /api/1/item")
    @allure.title("Повторное создание с теми же данными выдаёт разные UUID")
    def test_create_item_generates_unique_ids(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        first_response = item_client.create_item(payload)
        second_response = item_client.create_item(payload)

        try:
            assert first_response.status_code == 200
            assert second_response.status_code == 200
            first_id = extract_item_id_from_response(first_response)
            second_id = extract_item_id_from_response(second_response)
            assert first_id and second_id, "Не удалось извлечь UUID объявлений"
            assert (
                first_id != second_id
            ), "Два объявления с одинаковыми данными получили одинаковый UUID"
        finally:
            cleanup_item_if_created(item_client, first_response)
            cleanup_item_if_created(item_client, second_response)

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления без токена отклоняется")
    def test_create_item_without_token(
        self,
        access_token: str,
        registered_user: RegisteredUser,
    ) -> None:
        client = ItemClient()  # без токена
        payload = build_item_payload(seller_id=registered_user.id)
        response = client.create_item(payload)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с невалидным токеном отклоняется")
    def test_create_item_with_invalid_token(
        self,
        registered_user: RegisteredUser,
    ) -> None:
        client = ItemClient()
        client.set_bearer_token("invalid.token.value")
        payload = build_item_payload(seller_id=registered_user.id)
        response = client.create_item(payload)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с чужим sellerID отклоняется")
    def test_create_item_with_foreign_seller_id(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id + 1)
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert response.status_code == 400, (
            f"sellerID обязан совпадать с id пользователя из токена. "
            f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"
        )

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления без обязательного поля отклоняется")
    @pytest.mark.parametrize(
        "missing_field",
        ["sellerID", "name", "price", "statistics"],
    )
    def test_create_item_missing_required_field(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
        missing_field: str,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        payload.pop(missing_field)
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert response.status_code == 400, (
            f"Ожидали 400 при отсутствии поля '{missing_field}', "
            f"получили {response.status_code}. Ответ: {response.text}"
        )

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с пустым названием отклоняется")
    def test_create_item_empty_name(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id, overrides={"name": ""})
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с нулевой ценой отклоняется")
    def test_create_item_zero_price(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id, price=0)
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с отрицательной ценой отклоняется")
    def test_create_item_negative_price(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id, price=-100)
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert response.status_code == 400, (
            "BUG-01 (BUGS.md): сервис принял объявление с отрицательной ценой. "
            f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"
        )

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с отрицательной статистикой отклоняется")
    def test_create_item_negative_statistics(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        statistics = {"likes": -1, "viewCount": -2, "contacts": -3}
        payload = build_item_payload(seller_id=registered_user.id, statistics=statistics)
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert response.status_code == 400, (
            "BUG-02 (BUGS.md): сервис принял объявление с отрицательными "
            f"значениями статистики. Ожидали 400, получили "
            f"{response.status_code}. Ответ: {response.text}"
        )

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с неверным типом поля отклоняется")
    @pytest.mark.parametrize(
        "field, invalid_value",
        [
            ("sellerID", "abc"),
            ("price", "abc"),
            ("name", 123),
        ],
        ids=["sellerID строкой", "price строкой", "name числом"],
    )
    def test_create_item_invalid_field_type(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
        field: str,
        invalid_value: object,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id, overrides={field: invalid_value})
        response = item_client.create_item(payload)
        cleanup_item_if_created(item_client, response)
        assert response.status_code == 400, (
            f"Ожидали 400 для поля '{field}' со значением {invalid_value!r}, "
            f"получили {response.status_code}. Ответ: {response.text}"
        )

    @allure.story("POST /api/1/item")
    @allure.title("Создание объявления с пустым телом отклоняется")
    def test_create_item_empty_body(self, item_client: ItemClient) -> None:
        response = item_client.create_item({})
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    # ---------- GET /api/1/item/{id} ----------

    @allure.story("GET /api/1/item/{id}")
    @allure.title("Успешное получение объявления по id")
    def test_get_item_by_id_success(
        self,
        item_client: ItemClient,
        created_item: CreatedItem,
    ) -> None:
        response = item_client.get_item_by_id(created_item.id)

        assert (
            response.status_code == 200
        ), f"Ожидали 200, получили {response.status_code}. Ответ: {response.text}"
        item = find_item_by_id(parse_items(response), created_item.id)
        assert item is not None, "Объявление не найдено по id"
        assert item.sellerId == created_item.payload["sellerID"]
        assert item.name == created_item.payload["name"]
        assert item.price == created_item.payload["price"]
        assert item.statistics.model_dump() == created_item.payload["statistics"]

    @allure.story("GET /api/1/item/{id}")
    @allure.title("Получение объявления с невалидным форматом id отклоняется")
    def test_get_item_by_id_invalid_format(self, item_client: ItemClient) -> None:
        response = item_client.get_item_by_id("not-a-uuid")
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("GET /api/1/item/{id}")
    @allure.title("Получение несуществующего объявления возвращает 404")
    def test_get_item_by_id_not_found(self, item_client: ItemClient) -> None:
        response = item_client.get_item_by_id(Generator.generate_non_existent_uuid())
        assert (
            response.status_code == 404
        ), f"Ожидали 404, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("GET /api/1/item/{id}")
    @allure.title("Получение объявления без токена отклоняется")
    def test_get_item_by_id_without_token(
        self,
        item_client: ItemClient,
        created_item: CreatedItem,
    ) -> None:
        client = ItemClient()  # без токена
        response = client.get_item_by_id(created_item.id)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    # ---------- GET /api/1/{sellerID}/item ----------

    @allure.story("GET /api/1/{sellerID}/item")
    @allure.title("Успешное получение всех объявлений продавца")
    def test_get_items_by_seller_success(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
        created_item: CreatedItem,
    ) -> None:
        response = item_client.get_items_by_seller(registered_user.id)

        assert (
            response.status_code == 200
        ), f"Ожидали 200, получили {response.status_code}. Ответ: {response.text}"
        items = parse_items(response)
        item = find_item_by_id(items, created_item.id)
        assert item is not None, "Созданное объявление не найдено в списке объявлений продавца"
        assert item.sellerId == registered_user.id

    @allure.story("GET /api/1/{sellerID}/item")
    @allure.title("У продавца без объявлений возвращается пустой список")
    def test_get_items_by_seller_empty(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        response = item_client.get_items_by_seller(registered_user.id)
        assert response.status_code == 200
        assert response.json() == []

    @allure.story("GET /api/1/{sellerID}/item")
    @allure.title("Запрос объявлений продавца без токена отклоняется")
    def test_get_items_by_seller_without_token(
        self,
        registered_user: RegisteredUser,
    ) -> None:
        client = ItemClient()  # без токена
        response = client.get_items_by_seller(registered_user.id)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("GET /api/1/{sellerID}/item")
    @allure.title("Невалидный формат sellerID отклоняется")
    def test_get_items_by_seller_invalid_format(
        self,
        item_client: ItemClient,
    ) -> None:
        response = item_client.get_items_by_seller("abc")
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    # ---------- DELETE /api/2/item/{id} ----------

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Успешное удаление объявления")
    def test_delete_item_success(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        create_response = item_client.create_item(payload)
        assert create_response.status_code == 200
        item_id = extract_item_id_from_response(create_response)
        assert item_id

        delete_response = item_client.delete_item(item_id)
        assert delete_response.status_code == 200, (
            f"Ожидали 200, получили {delete_response.status_code}. "
            f"Ответ: {delete_response.text}"
        )

        get_response = item_client.get_item_by_id(item_id)
        assert get_response.status_code == 404, (
            "Объявление доступно после удаления: " f"{get_response.status_code} {get_response.text}"
        )

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Повторное удаление объявления возвращает 404")
    def test_delete_item_twice(
        self,
        item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        create_response = item_client.create_item(payload)
        assert create_response.status_code == 200
        item_id = extract_item_id_from_response(create_response)
        assert item_id

        first_delete = item_client.delete_item(item_id)
        assert first_delete.status_code == 200

        second_delete = item_client.delete_item(item_id)
        assert second_delete.status_code == 404, (
            f"Ожидали 404, получили {second_delete.status_code}. " f"Ответ: {second_delete.text}"
        )

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Удаление несуществующего объявления возвращает 404")
    def test_delete_item_not_found(self, item_client: ItemClient) -> None:
        response = item_client.delete_item(Generator.generate_non_existent_uuid())
        assert (
            response.status_code == 404
        ), f"Ожидали 404, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Тело ответа при удалении несуществующего объявления консистентно")
    def test_delete_item_not_found_response_body(
        self,
        item_client: ItemClient,
    ) -> None:
        response = item_client.delete_item(Generator.generate_non_existent_uuid())
        body = response.json()
        assert body.get("status") == str(response.status_code), (
            "BUG-04 (BUGS.md): HTTP-код и status в теле ответа различаются. "
            f"HTTP {response.status_code}, тело: {response.text}"
        )

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Удаление объявления с невалидным форматом id отклоняется")
    def test_delete_item_invalid_format(self, item_client: ItemClient) -> None:
        response = item_client.delete_item("not-a-uuid")
        assert (
            response.status_code == 400
        ), f"Ожидали 400, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Удаление объявления без токена отклоняется")
    def test_delete_item_without_token(
        self,
        item_client: ItemClient,
        created_item: CreatedItem,
    ) -> None:
        client = ItemClient()  # без токена
        response = client.delete_item(created_item.id)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("DELETE /api/2/item/{id}")
    @allure.title("Удаление чужого объявления запрещено")
    def test_delete_item_of_another_user_forbidden(
        self,
        item_client: ItemClient,
        second_item_client: ItemClient,
        registered_user: RegisteredUser,
    ) -> None:
        payload = build_item_payload(seller_id=registered_user.id)
        create_response = item_client.create_item(payload)
        assert create_response.status_code == 200
        item_id = extract_item_id_from_response(create_response)
        assert item_id

        try:
            delete_response = second_item_client.delete_item(item_id)
            assert delete_response.status_code in (401, 403), (
                "BUG-03 (BUGS.md): пользователь может удалить чужое объявление. "
                f"Ожидали 401/403, получили {delete_response.status_code}. "
                f"Ответ: {delete_response.text}"
            )
            get_response = item_client.get_item_by_id(item_id)
            assert (
                get_response.status_code == 200
            ), "BUG-03 (BUGS.md): объявление удалено другим пользователем"
        finally:
            item_client.delete_item(item_id)
