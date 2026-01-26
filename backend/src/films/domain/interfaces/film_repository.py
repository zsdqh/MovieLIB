import abc

from backend.src.films.domain.entities import Movie, Person


class IFilmRepository(abc.ABC):
    """Интерфейс репозитория для работы с фильмами и связанными таблицами"""

    @abc.abstractmethod
    async def get_film_by_id(self, movie_id: int) -> Movie:
        """Метод получения одного фильма"""

    @abc.abstractmethod
    async def get_person_by_id(self, person_id: int) -> Person:
        """Метод получения одного человека"""
