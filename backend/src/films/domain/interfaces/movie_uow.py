from abc import ABC

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.films.domain.interfaces.film_repository import IMovieRepository


class IMovieUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами и связанными сущностями"""

    films: IMovieRepository

    async def __aenter__(self) -> "IMovieUnitOfWork":
        """Вход в контекст единицы работы"""
        return self
