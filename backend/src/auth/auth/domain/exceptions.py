from backend.src.core.domain.exceptions import BadRequestException


class InvalidTokenException(BadRequestException):
    """Ошибка валидации токена"""

    detail = "Invalid token"
