from sqlalchemy import select

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_movie_repository import IGetMovieRepository
from backend.src.films.infrastructure.db.orm import Movie as MovieDB
from backend.src.films.infrastructure.utils.moviedb_to_domain import moviedb_to_domain


class PGGetMovieRepository(PGRepository, IGetMovieRepository):
    """Реализация репозитория для получения фильмов из БД"""

    async def get_film_by_id(self, movie_id: int) -> Movie | None:
        stmt = (
            select(MovieDB)
            .where(MovieDB.id == movie_id)
            .options(*MovieDB.get_load_options())
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj or obj.is_partial:
            return None
        return moviedb_to_domain(obj)

    async def get_films_by_id(self, movie_ids: list[int]) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_by_name(self, film_name: str) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_with_params(self, params: FilmParams) -> list[Movie]:
        raise NotImplementedError()

    async def get_random_film(self, params: RandomParams) -> Movie | None:
        raise NotImplementedError()
