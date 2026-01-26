from abc import ABC, abstractmethod

from backend.src.films.domain.dtos import MovieDTO, PersonDTO
from backend.src.films.domain.entities.filters import FilmParams, RandomParams


class IGetFilmRepository(ABC):
    """Интерфейс репозитория для получения фильмами"""

    @abstractmethod
    async def get_film_by_id(self, movie_id: int) -> MovieDTO | None:
        """Метод получения одного фильма"""

    @abstractmethod
    async def get_films_by_id(self, movie_ids: list[int]) -> list[MovieDTO]:
        """Получение сразу нескольких фильмов"""

    @abstractmethod
    async def get_films_by_name(self, film_name: str) -> list[MovieDTO]:
        """
        Получение фильмов по названию (частичное совпадение с полнотекстовым поиском)
        """

    @abstractmethod
    async def get_films_with_params(self, params: FilmParams) -> list[MovieDTO]:
        """Получение списка фильмов по заданным параметрам"""

    @abstractmethod
    async def get_random_film(self, params: RandomParams) -> MovieDTO | None:
        """Получение списка случайных фильмов по заданным параметрам"""

    @abstractmethod
    async def get_person_by_id(self, person_id: int) -> PersonDTO | None:
        """Получение информации о человеке"""

    @abstractmethod
    async def get_persons_by_id(self, person_ids: list[int]) -> list[PersonDTO]:
        """Получение информации о списке человек"""
