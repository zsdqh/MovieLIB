from typing import Any

from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork
from backend.src.films.infrastructure.external.multiple_tokens_getter import (
    MultipleTokensGetter,
)
from backend.src.films.infrastructure.external.posikkino_get_film_repository import (
    PoiskkinoGetMovieRepository,
)


class PoiskkinoMovieUnitOfWork(IGetMovieUnitOfWork):
    """
    Класс, реализующий интерфейс единицы работы с фильмами
    путем обращения к стороннему API
    """

    def __init__(self, client: MultipleTokensGetter) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        self.client = client

    async def __aenter__(self) -> IGetMovieUnitOfWork:
        self.films = PoiskkinoGetMovieRepository(self.client)
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass
