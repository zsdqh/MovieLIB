from abc import ABC

from backend.src.films.domain.interfaces.get_film_repository import IGetFilmRepository
from backend.src.users.domain.interfaces.uow import IUnitOfWork


class IGetFilmUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IGetFilmRepository

    async def rollback(self) -> None:
        raise NotImplementedError("Класс только для чтения, rollback не нужен")

    async def _commit(self) -> None:
        raise NotImplementedError("Класс только для чтения, _commit не нужен")

    async def __aenter__(self) -> "IGetFilmUnitOfWork":
        """Вход в контекст единицы работы"""
        return self
