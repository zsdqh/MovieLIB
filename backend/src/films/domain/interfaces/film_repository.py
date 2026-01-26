import abc

from backend.src.films.domain.entities.crud import (
    CreateMovie,
    CreatePerson,
)
from backend.src.films.domain.entities.entities import Country, Movie, Person


class IFilmRepository(abc.ABC):
    """Интерфейс репозитория для работы с фильмами и связанными таблицами"""

    @abc.abstractmethod
    async def get_film_by_id(self, movie_id: int) -> Movie:
        """Метод получения одного фильма"""

    @abc.abstractmethod
    async def get_person_by_id(self, person_id: int) -> Person:
        """Метод получения одного человека"""

    @abc.abstractmethod
    async def create_movie(self, movie_data: CreateMovie) -> Movie:
        """Метод создания фильма"""

    @abc.abstractmethod
    async def create_country(self, country_name: str) -> Country:
        """Метод для создания страны"""

    @abc.abstractmethod
    async def create_person(self, person_data: CreatePerson) -> Person:
        """Метод для создания человека"""
