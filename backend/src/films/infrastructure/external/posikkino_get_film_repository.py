from typing import Any

import httpx
from pydantic import ValidationError

from backend.src.core.domain.exceptions import NotFoundException
from backend.src.films.domain.dtos import MovieDTO
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_movie_repository import IGetMovieRepository
from backend.src.films.infrastructure.utils.movie_to_domain import movie_to_domain
from backend.src.films.infrastructure.utils.pydantic_to_api import pydantic_to_api

AnyDict = dict[str, Any]


class PoiskkinoGetMovieRepository(IGetMovieRepository):
    """Реализация репозитория для взаимодействия со сторонним API"""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Получение клиента для запросов по сети"""
        self.client = client

    async def get_film_by_id(self, movie_id: int) -> Movie | None:
        try:
            resp = await self.client.get(f"movie/{movie_id}")
            normalized = self._normalize_movie(dict(resp.json()))
            if not normalized:
                raise NotFoundException()
            return movie_to_domain(normalized)
        except NotFoundException as e:
            raise NotFoundException("Фильма с таким id не существует") from e

    async def get_films_by_id(self, movie_ids: list[int]) -> list[Movie]:
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
        movie_list = self._normalize_movie_list(data)
        return [movie_to_domain(normalized) for normalized in movie_list]

    async def get_films_by_name(self, film_name: str) -> list[Movie]:
        resp = await self.client.get("movie/search", params={"query": film_name})
        data = resp.json().get("docs", [])
        movie_list = self._normalize_movie_list(data)
        return [movie_to_domain(normalized) for normalized in movie_list]

    async def get_films_with_params(self, params: FilmParams) -> list[Movie]:
        resp = await self.client.get(
            "movie",
            params={
                "selectFields": self.select_fields,
                "notNullFields": self.not_null_fields,
                **self.default_params,
                **pydantic_to_api(params),
            },
        )
        data = resp.json().get("docs", [])
        movie_list = self._normalize_movie_list(data)
        return [movie_to_domain(normalized) for normalized in movie_list]

    async def get_random_film(self, params: RandomParams) -> Movie | None:
        resp = await self.client.get(
            "movie/random",
            params={
                "notNullFields": self.not_null_fields,
                **self.default_params,
                **pydantic_to_api(params),
            },
        )
        try:
            movie = self._normalize_movie(dict(resp.json()))
        except TypeError:
            # API отдал null, значит нет фильмов, подходящих условиям
            return None

        if not movie:
            return None

        return movie_to_domain(movie)

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
        persons = list(
            filter(
                lambda p: p.get("name") and p.get("photo"),
                movie_data.get("persons", []),
            )
        )
        movie_data["persons"] = persons
        sequels_and_prequels = list(
            filter(
                lambda f: f.get("poster") and f.get("poster").get("url"),
                movie_data.get("sequelsAndPrequels", []),
            )
        )
        movie_data["sequelsAndPrequels"] = sequels_and_prequels
        try:
            return MovieDTO.model_validate(movie_data)
        except ValidationError as e:
            for error in e.errors():
                # При ошибке валидации либо возвращаем None,
                # либо выбрасываем ошибку во вне (при неожиданной ситуации)
                if error.get("msg") == "Field required":
                    # Поле None, которое находится в списке not_null,
                    # значит фильм некорректен, возвращаем None
                    if error.get("loc")[0] not in self.not_null_fields:
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
        "poster",
    ]
