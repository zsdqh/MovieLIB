from typing import Any

import httpx

from backend.src.films.domain.dtos import MovieDTO, PersonDTO
from backend.src.films.domain.entities import FilmParams, RandomParams
from backend.src.films.domain.interfaces.film_repository import IFilmRepository


class PoiskkinoFilmRepository(IFilmRepository):
    """Реализация репозитория для взаимодействия со сторонним API"""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Передача клиента для запросов по сети"""
        self.client = client

    async def get_film(self, movie_id: int) -> MovieDTO:
        resp = await self.client.get(f"movie/{movie_id}")
        return MovieDTO.model_validate(self._normalize_movie(dict(resp.json())))

    async def get_films(self, movie_ids: list[int]) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_films_with_params(self, params: FilmParams) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_random_films(self, params: RandomParams) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_person(self, person_id: int) -> PersonDTO:
        raise NotImplementedError()

    async def get_persons(self, person_ids: list[int]) -> list[PersonDTO]:
        raise NotImplementedError()

    def _normalize_movie(self, movie_data: dict[str, Any]) -> dict[str, Any]:
        """Нормализация приходящих данных о фильме"""
        persons = list(filter(lambda p: p.get("name"), movie_data.get("persons", [])))
        movie_data["persons"] = persons
        return movie_data
