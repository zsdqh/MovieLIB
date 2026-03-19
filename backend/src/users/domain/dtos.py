"""Схемы передачи данных между функциями"""

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.src.users.domain.exceptions import (
    InvalidSortFieldException,
    TimestampException,
)


class UserBaseDTO(BaseModel):
    """Базовая схема пользователя"""

    username: str = Field(max_length=30)
    email: EmailStr


class UserRegisterDTO(UserBaseDTO):
    """Схема для регистрации пользователя"""

    password: str = Field(min_length=8, max_length=100)


class UserUpdateDTO(BaseModel):
    """Схема данных, которые пользователь может менять о себе"""

    username: str | None = Field(None, max_length=30)
    email: EmailStr | None = None


class UserPublicDTO(UserBaseDTO):
    """Возвращаемые, публично видимые данные о пользователе"""

    id: uuid.UUID
    is_admin: bool
    created_at: datetime.datetime


class UserRatingSetDTO(BaseModel):
    """Данные для выставления оценки фильму"""

    movie_id: int
    rating: int = Field(ge=1, le=10)


class UserRatingRemoveDTO(BaseModel):
    """Данные для удаления оценки фильма"""

    movie_id: int


class ListParams(BaseModel):
    """Параметры для фильтрации/сортировки/пагинации списка пользователей"""

    order_by: Optional[list[str]] = None
    created_before: Optional[datetime.datetime] = None
    page: int = Field(ge=0, default=0)
    size: int = Field(le=100, ge=1, default=20)

    @field_validator("created_before", mode="before")
    def forbid_timestamp(cls, time: str) -> str:
        """Проверка, не является ли время timestamp объектом"""
        if time.isdigit():
            raise TimestampException()
        return time

    @field_validator("order_by")
    def restrict_sortable_fields(
        cls, value: Optional[list[str]]
    ) -> Optional[list[str]]:
        """Разрешить сортировку только по заданным атрибутам"""
        if value is None:
            return None

        allowed_fields = ["created_at", "username"]
        for field_name in value:
            field_name = field_name.lstrip("-+")
            if field_name not in allowed_fields:
                raise InvalidSortFieldException(
                    detail=f"Сортировать можно только по следующим полям: "
                    f"{', '.join(allowed_fields)}"
                )
        return value
