"""Билдеры payload'ов на основе DTO-моделей.

Для негативных сценариев валидный базовый payload собирается через
Pydantic-модель, а затем точечно «ломается» через overrides/pop.
"""

from typing import Any, Dict, Optional

import allure

from src.models.auth import AutorizeRequest, RegisterRequest
from src.models.item import ItemCreateRequest, Statistics
from src.utils.generators import Generator


def build_register_payload(
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """Валидный payload для POST /api/1/register с уникальными данными."""
    with allure.step(
        f"Сборка payload для регистрации пользователя: username={username}, password={password}"
    ):
        request = RegisterRequest(
            username=username or Generator.generate_username(),
            password=password or Generator.generate_password(),
        )
        return request.model_dump()


def build_autorize_payload(username: str, password: str) -> Dict[str, Any]:
    """Payload для POST /api/1/autorize."""
    return AutorizeRequest(username=username, password=password).model_dump()


def build_item_payload(
    seller_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    statistics: Optional[Dict[str, int]] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Валидный payload для POST /api/1/item.

    sellerID обязан совпадать с id пользователя из bearer-токена,
    поэтому передаётся явно.
    """
    with allure.step(
        f"Сборка payload для создания объявления: seller_id={seller_id}, "
        f"name={name}, price={price}, statistics={statistics}, overrides={overrides}"
    ):
        request = ItemCreateRequest(
            sellerID=seller_id,
            name=name or Generator.generate_item_name(),
            price=price if price is not None else Generator.generate_price(),
            statistics=Statistics(**(statistics or Generator.generate_statistics())),
        )
        payload = request.model_dump()
        if overrides:
            payload.update(overrides)
        return payload
