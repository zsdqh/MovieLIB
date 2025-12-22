from typing import Any


class DomainException(Exception):
    """
    Доменная ошибка, позволяющая передавать деталь и дополнительные параметры
    нужна для корректного отлавливания ошибок внутри проекта
    """

    detail: Any | None = "Ошибка сервера"

    def __init__(self, detail: Any | None = None) -> None:
        if detail:
            self.detail = detail

    def __str__(self) -> str:
        return str(self.detail)


class NotFoundException(DomainException):
    """Объект не найден"""

    detail = "Объект не найден"


class BadRequestException(DomainException):
    """Ошибка со стороны пользователя"""

    detail = "Плохой запрос"


class AlreadyExistsException(DomainException):
    """Объект уже существует"""

    detail = "Объект уже существует"


class AccessDeniedException(DomainException):
    """У пользователя нет прав на выполнение действия"""

    detail = "У вас нет прав на это действие"


class UnauthorizedException(DomainException):
    """Пользователь не авторизован"""

    detail = "Вам нужно авторизоваться"
