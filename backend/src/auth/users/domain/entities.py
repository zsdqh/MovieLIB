"""Сущности с корректными данными для работы функций"""

import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Стандартные поля моделей пользователя"""

    email: str
    username: str = Field(min_length=3)


class User(UserBase):
    """Модель для передачи объекта из БД между функциями"""

    id: uuid.UUID
    hashed_password: str
    created_at: datetime.datetime
    valid_refresh_id: int
    avatar_url: str | None = None
    is_activated: bool
    is_blocked: bool
    is_admin: bool


class UserRegister(UserBase):
    """Данные для регистрации пользователя"""

    hashed_password: str


class UserUpdate(BaseModel):
    """
    Изменяемые данные пользователя
    None - поле не будет изменено
    """

    id: uuid.UUID
    email: EmailStr | None = None
    username: str | None = None
    hashed_password: str | None = None
    valid_refresh_id: int | None = None
    is_activated: bool | None = None
    is_admin: bool | None = None
    avatar_url: str | None = None


class UserPublic(UserBase):
    """Данные о пользователе, выводимые в ответах"""

    id: uuid.UUID
    created_at: datetime.datetime
    avatar_url: str | None = None
    is_activated: bool
    is_blocked: bool
    is_admin: bool
