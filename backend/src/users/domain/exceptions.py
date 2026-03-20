"""Кастомные ошибки для вывода пользователю"""

import json

from pydantic_core import ValidationError

from backend.src.core.domain.exceptions import (
    BadRequestException,
    NotFoundException,
)


class InvalidSortFieldException(BadRequestException):
    """Ошибка при введении неправильных полей для сортировки"""


class ValidationCustomException(BadRequestException):
    """Ошибка валидации данных, введенных пользователем"""

    def __init__(self, validation_error: ValidationError) -> None:
        """
        Приведение ValidationError к человекочитаемому виду
        :param validation_error: ошибка, посылаемая валидатором
        """
        error_dict = json.loads(validation_error.json())[0]
        detail = {
            "invalid_fields": error_dict.get("loc"),
            "message": error_dict.get("msg"),
        }
        super().__init__(detail=detail)


class TimestampException(BadRequestException):
    """
    Ошибка при передаче timestamp вместо datetime,
    так как ORM корректно работает только с datetime
    """

    detail = "Timestapmp объекты не разрешены, используйте даты в формате ISO 8601"


class RatingException(BadRequestException):
    """Ошибка значения рейтинга от 1 до 10"""

    detail = "Рейтинг может иметь только значения от 1 до 10"


class ListNotFoundException(NotFoundException):
    """Ошибка, говорящая о том, что фильм не найден"""

    def __init__(self, list_id: int) -> None:
        self.detail = f"Список с id={list_id} не найден"
        super().__init__(detail=self.detail)
