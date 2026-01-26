from abc import ABC

from backend.src.films.domain.interfaces.film_repository import IFilmRepository
from backend.src.users.domain.interfaces.uow import IUnitOfWork


class IFilmUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IFilmRepository

    async def __aenter__(self) -> "IFilmUnitOfWork":
        """Вход в контекст единицы работы"""
        return self
