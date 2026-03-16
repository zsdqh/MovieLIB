from backend.src.core.domain.exceptions import DomainException, NotFoundException


class RequestLimitExceededException(DomainException):
    """Внутренняя ошибка, говорящая, что лимит запросов кончился"""

    detail = "Достигнут лимит запросов для текущего токена"


class MovieNotFoundException(NotFoundException):
    """Ошибка, говорящая о том, что фильм не найден"""

    def __init__(self, movie_id: int) -> None:
        self.detail = f"Фильм с id={movie_id} не найден"
        super().__init__(detail=self.detail)
