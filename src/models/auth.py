"""DTO-модели для ручек регистрации и авторизации."""

from typing import Any, Dict

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """Тело запроса POST /api/1/register."""

    username: str
    password: str


class RegisterResponse(BaseModel):
    """Ответ POST /api/1/register при успехе (201)."""

    id: int
    username: str


class RegisteredUser(BaseModel):
    """Данные зарегистрированного пользователя для тестов."""

    id: int
    username: str
    password: str


class CreatedItem(BaseModel):
    """Данные созданного объявления для тестов."""

    id: str
    payload: Dict[str, Any]


class AutorizeRequest(BaseModel):
    """Тело запроса POST /api/1/autorize."""

    username: str
    password: str


class AutorizeResponse(BaseModel):
    """Ответ POST /api/1/autorize при успехе (200)."""

    accessToken: str
    tokenType: str


class AuthErrorResponse(BaseModel):
    """Тело ошибки публичных ручек (register/autorize)."""

    error: str
