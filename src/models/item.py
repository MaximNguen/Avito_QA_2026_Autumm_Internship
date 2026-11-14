"""DTO-модели для ручек объявлений и статистики."""

from typing import Any, Optional, Union

from pydantic import BaseModel


class Statistics(BaseModel):
    """Статистика объявления."""

    likes: int
    viewCount: int
    contacts: int


class ItemCreateRequest(BaseModel):
    """Тело запроса POST /api/1/item."""

    sellerID: int
    name: str
    price: int
    statistics: Statistics


class ItemCreateResponse(BaseModel):
    """Ответ POST /api/1/item при успехе (200)."""

    status: str


class Item(BaseModel):
    """Объявление в ответах GET /api/1/item/{id} и GET /api/1/{sellerID}/item."""

    id: str
    sellerId: int
    name: str
    price: int
    createdAt: str
    statistics: Statistics


class ErrorResult(BaseModel):
    """Детали ошибки защищённых ручек."""

    message: Optional[str] = None
    messages: Optional[Union[dict, list, Any]] = None


class ApiErrorResponse(BaseModel):
    """Тело ошибки защищённых ручек (item/statistic)."""

    result: ErrorResult
    status: str
