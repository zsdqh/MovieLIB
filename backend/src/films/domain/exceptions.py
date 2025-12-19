from backend.src.core.domain.exceptions import DomainException


class RequestLimitExceededException(DomainException):
    """Внутренняя ошибка, говорящая, что лимит запросов кончился"""

    detail = "Request limit for current token exceeded"
