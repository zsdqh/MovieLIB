from typing import Any

import httpx
from pydantic import ValidationError

from backend.src.films.domain.dtos import MovieDTO, PersonDTO
from backend.src.films.domain.entities import FilmParams, RandomParams
from backend.src.films.domain.interfaces.film_repository import IFilmRepository

AnyDict = dict[str, Any]


class PoiskkinoFilmRepository(IFilmRepository):
    """Реализация репозитория для взаимодействия со сторонним API"""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Передача клиента для запросов по сети"""
        self.client = client

    async def get_film_by_id(self, movie_id: int) -> MovieDTO | None:
        resp = await self.client.get(f"movie/{movie_id}")
        return self._normalize_movie(dict(resp.json()))

    async def get_films_by_id(self, movie_ids: list[int]) -> list[MovieDTO]:
        if not movie_ids:
            return []

        resp = await self.client.get(
            "movie",
            params={
                "id": movie_ids,
                "selectFields": self.select_fields,
            },
        )
        data = resp.json().get("docs", [])
        return self._normalize_movie_list(data)

    async def get_films_by_name(self, film_name: str) -> list[MovieDTO]:
        resp = await self.client.get("movie/search", params={"query": film_name})
        data = resp.json().get("docs", [])
        return self._normalize_movie_list(data)

    async def get_films_with_params(self, params: FilmParams) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_random_films(self, params: RandomParams) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_person_by_id(self, person_id: int) -> PersonDTO | None:
        resp = await self.client.get(f"person/{person_id}")
        return self._normalize_person(dict(resp.json()))

    async def get_persons_by_id(self, person_ids: list[int]) -> list[PersonDTO]:
        if not person_ids:
            return []
        resp = await self.client.get(
            "person",
            params={"id": person_ids, "selectFields": self.select_person_fields},
        )
        data = resp.json().get("docs", [])
        return self._normalize_person_list(data)

    def _normalize_movie_list(self, movie_list: list[AnyDict]) -> list[MovieDTO]:
        """Нормализация списка фильмов"""
        res = []
        for movie in movie_list:
            normal = self._normalize_movie(movie)
            if not normal:
                continue
            res.append(normal)
        return res

    def _normalize_movie(self, movie_data: AnyDict) -> MovieDTO | None:
        """Нормализация приходящих данных о фильме"""
        persons = list(filter(lambda p: p.get("name"), movie_data.get("persons", [])))
        movie_data["persons"] = persons
        try:
            return MovieDTO.model_validate(movie_data)
        except ValidationError as e:
            for error in e.errors():
                if error.get("input") is None:
                    if error.get("loc")[0] not in self.not_null_fields:
                        raise
                else:
                    raise
            return None

    def _normalize_person_list(self, person_list: list[AnyDict]) -> list[PersonDTO]:
        """Нормализация списка фильмов"""
        res = []
        for person in person_list:
            normal = self._normalize_person(person)
            if not normal:
                continue
            res.append(normal)
        return res

    def _normalize_person(self, person_data: AnyDict) -> PersonDTO | None:
        """Нормализация приходящих данных о людях"""
        try:
            return PersonDTO.model_validate(person_data)
        except ValidationError as e:
            for error in e.errors():
                if error.get("input") is None:
                    if error.get("loc")[0] not in self.not_null_person_fields:
                        raise
                else:
                    raise
            return None

    # Стандартные параметры поиска случайных фильмов
    default_params = {"rating.kp": "6.5-10"}

    # Поля, которые необходимо получить из стороннего api для уменьшения размера ответа
    select_fields = [
        "id",
        "name",
        "description",
        "shortDescription",
        "slogan",
        "type",
        "isSeries",
        "year",
        "rating",
        "ageRating",
        "movieLength",
        "seriesLength",
        "genres",
        "countries",
        "poster",
        "backdrop",
        "persons",
        "sequelsAndPrequels",
    ]

    # Поля, которые не должны быть None при поиске в api
    not_null_fields = [
        "id",
        "name",
        "description",
        "type",
        "year",
        "rating.kp",
        "poster.url",
        "poster",
        "rating",
    ]

    not_null_person_fields = ["id", "photo", "name", "enProfession", "birthday"]

    select_person_fields = [
        "id",
        "name",
        "photo",
        "birthday",
        "movies",
    ]
