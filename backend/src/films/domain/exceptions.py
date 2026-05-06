from backend.src.core.domain.exceptions import DomainException, NotFoundException
from backend.src.films.domain.entities.entities import ExternalExceptionData


class RequestLimitExceededException(DomainException):
    """Внутренняя ошибка, говорящая, что лимит запросов кончился"""

    detail = "Достигнут лимит запросов для текущего токена"


class MovieNotFoundException(NotFoundException):
    """Ошибка, говорящая о том, что фильм не найден"""

    def __init__(self, movie_id: int) -> None:
        self.detail = f"Фильм с id={movie_id} не найден"
        super().__init__(detail=self.detail)


class PersonNotFoundException(NotFoundException):
    """Ошибка, говорящая о том, что фильм не найден"""

    def __init__(self, movie_id: int) -> None:
        self.detail = f"Человек с id={movie_id} не найден"
        super().__init__(detail=self.detail)


class CustomValidationException(DomainException):
    """Ошибка, говорящая о неправильности данных"""


class ExternalException(DomainException):
    """Ошибка из внешнего сервиса"""

    def __init__(self, exception_data: ExternalExceptionData):
        self.detail = "\n".join(exception_data.message)
        super().__init__(detail=self.detail)


class NotEnoughDataException(DomainException):
    """Ошибка, говорящая о том, что данных недостаточно"""

    detail = "Невозможно отобразить фильм, так как данные о нем неполны"
