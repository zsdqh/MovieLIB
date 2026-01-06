from typing import Any

from httpx import AsyncClient

from backend.src.films.domain.interfaces.film_unit_of_work import IFilmUnitOfWork
from backend.src.films.infrastructure.external.posikkino_film_repository import (
    PoiskkinoFilmRepository,
)


class PoiskkinoUnitOfWork(IFilmUnitOfWork):
    """
    Класс, реализующий интерфейс единицы работы с фильмами
    путем обращения к стороннему API
    """

    def __init__(self, client: AsyncClient) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        self.client = client

    async def __aenter__(self) -> IFilmUnitOfWork:
        client = await self.client.__aenter__()
        self.films = PoiskkinoFilmRepository(client)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.__aexit__(*args)
