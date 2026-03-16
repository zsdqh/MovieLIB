import abc

from backend.src.films.domain.entities.crud import (
    CreateMovie,
    CreatePerson,
)
from backend.src.films.domain.entities.entities import Movie, Person


class IMovieRepository(abc.ABC):
    """Интерфейс репозитория для работы с фильмами и связанными таблицами"""

    @abc.abstractmethod
    async def create_movie(
        self, movie_data: CreateMovie, related_group_id: int | None = None
    ) -> Movie:
        """Метод создания фильма"""

    @abc.abstractmethod
    async def create_person(self, person_data: CreatePerson) -> Person:
        """Метод для создания человека"""
