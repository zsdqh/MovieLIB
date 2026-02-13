from abc import ABC, abstractmethod

from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams


class IGetFilmRepository(ABC):
    """Интерфейс репозитория для получения фильмами"""

    @abstractmethod
    async def get_film_by_id(self, movie_id: int) -> Movie | None:
        """Метод получения одного фильма"""

    @abstractmethod
    async def get_films_by_id(self, movie_ids: list[int]) -> list[Movie]:
        """Получение сразу нескольких фильмов"""

    @abstractmethod
    async def get_films_by_name(self, film_name: str) -> list[Movie]:
        """
        Получение фильмов по названию (частичное совпадение с полнотекстовым поиском)
        """

    @abstractmethod
    async def get_films_with_params(self, params: FilmParams) -> list[Movie]:
        """Получение списка фильмов по заданным параметрам"""

    @abstractmethod
    async def get_random_film(self, params: RandomParams) -> Movie | None:
        """Получение списка случайных фильмов по заданным параметрам"""
