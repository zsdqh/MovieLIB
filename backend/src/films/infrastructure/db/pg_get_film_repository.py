from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_film_repository import IGetFilmRepository


class PGGetFilmRepository(PGRepository, IGetFilmRepository):
    """Реализация репозитория для получения фильмов из БД"""

    async def get_film_by_id(self, movie_id: int) -> Movie | None:
        raise NotImplementedError()

    async def get_films_by_id(self, movie_ids: list[int]) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_by_name(self, film_name: str) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_with_params(self, params: FilmParams) -> list[Movie]:
        raise NotImplementedError()

    async def get_random_film(self, params: RandomParams) -> Movie | None:
        raise NotImplementedError()
