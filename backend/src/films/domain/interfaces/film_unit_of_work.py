import abc
from abc import ABC

from backend.src.films.domain.interfaces.get_film_repository import IGetFilmRepository
from backend.src.films.domain.interfaces.uow import IUnitOfWork


class IGetFilmUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IGetFilmRepository

    @abc.abstractmethod
    async def __aenter__(self) -> "IGetFilmUnitOfWork":
        pass
