from abc import ABC

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.films.domain.interfaces.film_repository import IFilmRepository


class IFilmUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IFilmRepository

    async def __aenter__(self) -> "IFilmUnitOfWork":
        """Вход в контекст единицы работы"""
        return self
