from abc import ABC

from backend.src.films.domain.interfaces.film_repository import IFilmRepository
from backend.src.films.domain.interfaces.uow import IUnitOfWork


class IFilmUnitOfWork(IUnitOfWork, ABC):
    """Интерфейс единицы работы с фильмами"""

    films: IFilmRepository
