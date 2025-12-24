from backend.src.core.domain.exceptions import BadRequestException


class WrongCodeException(BadRequestException):
    """Ошибка передачи неправильного кода подтверждения"""
