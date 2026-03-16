from abc import ABC

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.films.domain.interfaces.get_movie_repository import IGetMovieRepository


class IGetMovieUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IGetMovieRepository

    async def rollback(self) -> None:
        raise NotImplementedError("Класс только для чтения, rollback не нужен")

    async def _commit(self) -> None:
        raise NotImplementedError("Класс только для чтения, _commit не нужен")

    async def __aenter__(self) -> "IGetMovieUnitOfWork":
        """Вход в контекст единицы работы"""
        return self
