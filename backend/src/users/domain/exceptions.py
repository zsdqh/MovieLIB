"""Кастомные ошибки для вывода пользователю"""

import json

from pydantic_core import ValidationError

from backend.src.core.domain.exceptions import (
    BadRequestException,
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
