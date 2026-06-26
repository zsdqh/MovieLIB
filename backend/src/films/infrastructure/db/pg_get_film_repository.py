from sqlalchemy import func, or_, select
from sqlalchemy.orm import aliased

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_movie_repository import IGetMovieRepository
from backend.src.films.infrastructure.db.orm import Movie as MovieDB
from backend.src.films.infrastructure.db.orm import movie_genre_table
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

    async def get_similar_films(self, movie_id: int) -> list[Movie]:
        input_movie = aliased(MovieDB)
        input_subq = (
            select(input_movie.id, input_movie.group_id)
            .where(input_movie.id == movie_id)
            .subquery()
        )
        input_mg = aliased(movie_genre_table)
        mg = aliased(movie_genre_table)

        # Подзапрос: считаем общие жанры и фильтруем по группе
        shared_genre_subq = (
            select(
                MovieDB.id,
                func.count(mg.c.genre_id).label(  # pylint: disable=not-callable
                    "shared_genres"
                ),
            )
            .join(mg, MovieDB.id == mg.c.movie_id)
            .join(input_mg, mg.c.genre_id == input_mg.c.genre_id)
            .join(input_subq, input_mg.c.movie_id == input_subq.c.id)
            .where(
                MovieDB.id != movie_id,
                or_(
                    input_subq.c.group_id.is_(None),
                    MovieDB.group_id.is_distinct_from(input_subq.c.group_id),
                ),
            )
            .group_by(MovieDB.id)
            .subquery()
        )

        # Основной запрос: подгружаем все связи MovieDB без GROUP BY
        query = (
            select(MovieDB)
            .limit(10)
            .join(shared_genre_subq, MovieDB.id == shared_genre_subq.c.id)
            .options(*MovieDB.get_load_options())
            .order_by(
                shared_genre_subq.c.shared_genres.desc(),
                MovieDB.kp_rating.desc(),
            )
        )

        res = await self.session.execute(query)
        movies = res.scalars().all()  # получаем экземпляры MovieDB

        return [moviedb_to_domain(movie) for movie in movies]

    async def get_random_films(self, page: int) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_by_id(self, movie_ids: list[int]) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_by_name(self, film_name: str, page: int) -> list[Movie]:
        raise NotImplementedError()

    async def get_films_with_params(self, params: FilmParams, page: int) -> list[Movie]:
        raise NotImplementedError()

    async def get_random_film(self, params: RandomParams) -> Movie | None:
        raise NotImplementedError()
