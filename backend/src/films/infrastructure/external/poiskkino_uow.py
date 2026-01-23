from typing import Any

from httpx import AsyncClient

from backend.src.films.domain.interfaces.film_unit_of_work import IGetFilmUnitOfWork
from backend.src.films.infrastructure.external.posikkino_film_repository import (
    PoiskkinoGetFilmRepository,
)


class PoiskkinoUnitOfWork(IGetFilmUnitOfWork):
    """
    Класс, реализующий интерфейс единицы работы с фильмами
    путем обращения к стороннему API
    """

    def __init__(self, client: AsyncClient) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        self.client = client

    async def __aenter__(self) -> IGetFilmUnitOfWork:
        self.films = PoiskkinoGetFilmRepository(self.client)
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass
