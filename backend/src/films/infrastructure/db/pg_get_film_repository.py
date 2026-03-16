from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_movie_repository import IGetMovieRepository
from backend.src.films.infrastructure.db.orm import Movie as MovieDB
from backend.src.films.infrastructure.db.orm import PersonMovie as PersonMovieDB
from backend.src.films.infrastructure.db.orm import RelatedGroup as RelatedGroupDB
from backend.src.films.infrastructure.utils.moviedb_to_domain import moviedb_to_domain


class PGGetMovieRepository(PGRepository, IGetMovieRepository):
    """Реализация репозитория для получения фильмов из БД"""

    select_options = (
        selectinload(MovieDB.genres),
        selectinload(MovieDB.countries),
        selectinload(MovieDB.person_movies).selectinload(PersonMovieDB.person),
        selectinload(MovieDB.person_movies).selectinload(PersonMovieDB.profession),
        selectinload(MovieDB.related_group).selectinload(RelatedGroupDB.movies),
    )

    async def get_film_by_id(self, movie_id: int) -> Movie | None:
        stmt = (
            select(MovieDB).where(MovieDB.id == movie_id).options(*self.select_options)
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
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
