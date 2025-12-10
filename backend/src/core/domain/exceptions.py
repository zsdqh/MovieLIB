from typing import Any, Optional


class DomainException(Exception):
    """
    Доменная ошибка, позволяющая передавать деталь и дополнительные параметры
    нужна для корректного отлавливания ошибок внутри проекта
    """

    detail: str | dict[str, Any] = "Server error"

    def __init__(self, detail: Optional[str | dict[str, Any]] = None) -> None:
        if detail:
            self.detail = detail


class NotFoundException(DomainException):
    """Объект не найден"""

    detail = "Object not found"


class BadRequestException(DomainException):
    """Ошибка со стороны пользователя"""

    detail = "Bad request"


class AlreadyExistsException(DomainException):
    """Объект уже существует"""

    detail = "Object already exists"


class AccessDeniedException(DomainException):
    """У пользователя нет прав на выполнение действия"""

    detail = "You are not allowed to do this"


class UnauthorizedException(DomainException):
    """Пользователь не авторизован"""

    detail = "You need to authorize first"
