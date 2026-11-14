"""Тесты ручек статистики: GET /api/1/statistic/{id} и GET /api/2/statistic/{id}."""

import allure
import pytest

from src.clients.item_client import ItemClient
from src.clients.statistic_client import StatisticClient
from src.models.item import Statistics
from src.utils.generators import Generator
from src.models.auth import CreatedItem


def get_statistic(client: StatisticClient, version: str, item_id: str):
    """Вызвать ручку статистики нужной версии."""
    return getattr(client, f"get_statistic_{version}")(item_id)


@allure.feature("Статистика")
class TestStatisticAPI:
    """Позитивные и негативные проверки обеих версий ручки статистики."""

    @allure.story("GET /api/1/statistic/{id}")
    @allure.title("Статистика v1 соответствует данным созданного объявления")
    def test_get_statistic_v1_success(
        self,
        statistic_client: StatisticClient,
        created_item: CreatedItem,
    ) -> None:
        response = statistic_client.get_statistic_v1(created_item.id)

        assert (
            response.status_code == 200
        ), f"Ожидали 200, получили {response.status_code}. Ответ: {response.text}"
        body = response.json()
        assert (
            isinstance(body, list) and len(body) == 1
        ), "Ожидали массив из одного элемента со статистикой"
        statistic = Statistics.model_validate(body[0])
        assert statistic.model_dump() == created_item.payload["statistics"]

    @allure.story("GET /api/2/statistic/{id}")
    @allure.title("Статистика v2 соответствует данным созданного объявления")
    def test_get_statistic_v2_success(
        self,
        statistic_client: StatisticClient,
        created_item: CreatedItem,
    ) -> None:
        response = statistic_client.get_statistic_v2(created_item.id)

        assert (
            response.status_code == 200
        ), f"Ожидали 200, получили {response.status_code}. Ответ: {response.text}"
        body = response.json()
        assert (
            isinstance(body, list) and len(body) == 1
        ), "Ожидали массив из одного элемента со статистикой"
        statistic = Statistics.model_validate(body[0])
        assert statistic.model_dump() == created_item.payload["statistics"]

    @allure.story("GET /api/2/statistic/{id}")
    @allure.title("Статистика v1 и v2 возвращают одинаковые данные")
    def test_statistic_v1_and_v2_are_same(
        self,
        statistic_client: StatisticClient,
        created_item: CreatedItem,
    ) -> None:
        response_v1 = statistic_client.get_statistic_v1(created_item.id)
        response_v2 = statistic_client.get_statistic_v2(created_item.id)

        assert response_v1.status_code == 200
        assert response_v2.status_code == 200
        assert response_v1.json() == response_v2.json(), (
            "Данные статистики v1 и v2 различаются: " f"{response_v1.text} != {response_v2.text}"
        )

    @allure.story("GET /api/1/statistic/{id}")
    @allure.title("Статистика по несуществующему id возвращает 404")
    @pytest.mark.parametrize("version", ["v1", "v2"])
    def test_get_statistic_not_found(
        self,
        statistic_client: StatisticClient,
        version: str,
    ) -> None:
        item_id = Generator.generate_non_existent_uuid()
        response = get_statistic(statistic_client, version, item_id)
        assert (
            response.status_code == 404
        ), f"Ожидали 404, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("GET /api/1/statistic/{id}")
    @allure.title("Статистика с невалидным форматом id отклоняется")
    @pytest.mark.parametrize("version", ["v1", "v2"])
    def test_get_statistic_invalid_format(
        self,
        statistic_client: StatisticClient,
        version: str,
    ) -> None:
        response = get_statistic(statistic_client, version, "not-a-uuid")
        assert response.status_code == 400, (
            f"BUG-06 (BUGS.md): ручка {version} на невалидный формат id "
            f"ответила {response.status_code} вместо 400 "
            f"(v1 при этом возвращает 400). Ответ: {response.text}"
        )

    @allure.story("GET /api/1/statistic/{id}")
    @allure.title("Запрос статистики без токена отклоняется")
    @pytest.mark.parametrize("version", ["v1", "v2"])
    def test_get_statistic_without_token(
        self,
        statistic_client: StatisticClient,
        created_item: CreatedItem,
        version: str,
    ) -> None:
        client = StatisticClient()  # без токена
        response = get_statistic(client, version, created_item.id)
        assert (
            response.status_code == 401
        ), f"Ожидали 401, получили {response.status_code}. Ответ: {response.text}"

    @allure.story("GET /api/1/statistic/{id}")
    @allure.title("Статистика удалённого объявления недоступна")
    @pytest.mark.parametrize("version", ["v1", "v2"])
    def test_get_statistic_after_item_deleted(
        self,
        statistic_client: StatisticClient,
        item_client: ItemClient,
        created_item: CreatedItem,
        version: str,
    ) -> None:
        delete_response = item_client.delete_item(created_item.id)
        assert delete_response.status_code == 200

        response = get_statistic(statistic_client, version, created_item.id)
        assert response.status_code == 404, (
            f"BUG-05 (BUGS.md): статистика {version} доступна после удаления "
            f"объявления. Ожидали 404, получили {response.status_code}. "
            f"Ответ: {response.text}"
        )
