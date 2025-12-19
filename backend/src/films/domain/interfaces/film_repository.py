from abc import ABC, abstractmethod

from backend.src.films.domain.dtos import MovieDTO, PersonDTO
from backend.src.films.domain.entities import FilmParams, RandomParams


class IFilmRepository(ABC):
    """Интерфейс репозитория для работы с фильмами"""

    @abstractmethod
    async def get_film(self, movie_id: int) -> MovieDTO:
        """Метод получения одного фильма"""

    @abstractmethod
    async def get_films(self, movie_ids: list[int]) -> list[MovieDTO]:
        """Получение сразу нескольких фильмов"""

    @abstractmethod
    async def get_films_with_params(self, params: FilmParams) -> list[MovieDTO]:
        """Получение списка фильмов по заданным параметрам"""

    @abstractmethod
    async def get_random_films(self, params: RandomParams) -> list[MovieDTO]:
        """Получение списка случайных фильмов по заданным параметрам"""

    @abstractmethod
    async def get_person(self, person_id: int) -> PersonDTO:
        """Получение информации о человеке"""

    @abstractmethod
    async def get_persons(self, person_ids: list[int]) -> list[PersonDTO]:
        """Получение информации о списке человек"""
