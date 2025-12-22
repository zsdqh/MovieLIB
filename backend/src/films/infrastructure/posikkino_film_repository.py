from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from backend.src.core.domain.exceptions import NotFoundException
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
        try:
            resp = await self.client.get(f"movie/{movie_id}")
            return self._normalize_movie(dict(resp.json()))
        except NotFoundException:
            return None

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
        resp = await self.client.get(
            "movie",
            params={
                "selectFields": self.select_fields,
                "notNullFields": self.not_null_fields,
                **self.default_params,
                **self._base_model_to_api_format(params),
            },
        )
        data = resp.json().get("docs", [])
        return self._normalize_movie_list(data)

    async def get_random_film(self, params: RandomParams) -> MovieDTO | None:
        resp = await self.client.get(
            "movie/random",
            params={
                "notNullFields": self.not_null_fields,
                **self.default_params,
                **self._base_model_to_api_format(params),
            },
        )
        try:
            movie = self._normalize_movie(dict(resp.json()))
        except TypeError:
            # API отдал null, значит нет фильмов, подходящих условиям
            return None

        if not movie:
            # фильм не прошел нормализацию(практически никогда),
            # просто получаем новый рекурсивно
            movie = await self.get_random_film(params=params)
        return movie

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
                # При ошибке валидации либо возвращаем None,
                # либо выбрасываем ошибку во вне (при неожиданной ситуации)
                if error.get("input") is None:
                    # Поле None, которое находится в списке not_null,
                    # значит фильм некорректен, возвращаем None
                    if error.get("loc")[0] not in self.not_null_fields:
                        raise
                else:
                    raise
            return None

    def _normalize_person_list(self, person_list: list[AnyDict]) -> list[PersonDTO]:
        """Нормализация списка людей"""
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

    def _base_model_to_api_format(self, model: BaseModel) -> AnyDict:
        """
        Преобразование базовой модели pydantic с snake_case нотацией
        в dict с camelCase нотацией и валидными ключами для стороннего API
        """
        res = {}
        for name, value in model:
            if value is None:
                continue
            if name in ["genres", "countries"]:
                name += ".name"
            if name == "rating":
                name += ".kp"

            camel_name = []

            # убираем нижние подчеркивания и делаем следующую букву большой
            # буквально превращаем snake_case в camelCase
            f = False
            for char in name:
                if char == "_":
                    f = True
                else:
                    camel_name.append(char if not f else char.upper())
                    f = False
            res["".join(camel_name)] = value
        return res

    # Стандартные параметры поиска случайных фильмов
    default_params = {"rating.kp": "6.5-10"}

    # Поля, которые необходимо получить из стороннего api для уменьшения размера ответа
    select_fields = [
        "id",
        "name",
        "description",
        "shortDescription",
        "slogan",
        "typeNumber",
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
        "typeNumber",
        "year",
        "rating.kp",
        "poster.url",
    ]

    not_null_person_fields = ["id", "photo", "name", "enProfession", "birthday"]

    select_person_fields = [
        "id",
        "name",
        "photo",
        "birthday",
        "movies",
    ]
