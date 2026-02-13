from typing import Any

from httpx import AsyncClient

from backend.src.films.domain.interfaces.get_person_uow import IGetPersonUnitOfWork
from backend.src.films.infrastructure.external.poiskkino_get_person_repository import (
    PoiskkinoGetPersonRepository,
)


class PoiskkinoPersonUnitOfWork(IGetPersonUnitOfWork):
    """
    Класс, реализующий интерфейс единицы работы с фильмами
    путем обращения к стороннему API
    """

    def __init__(self, client: AsyncClient) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        self.client = client

    async def __aenter__(self) -> IGetPersonUnitOfWork:
        self.persons = PoiskkinoGetPersonRepository(self.client)
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass
