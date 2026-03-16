from backend.src.films.application.movie_use_case import MovieUseCase
from backend.src.films.domain.entities.crud import CreateMovie
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.exceptions import MovieNotFoundException


class GetMovieUseCase(MovieUseCase):
    """Получение данных о фильме"""

    async def __call__(self, movie_id: int) -> Movie:
        """
        Сначала фильм берется из внутреннего хранилища, если не найден,
        то данные берутся из внешнего api и помещаются во внутреннее хранилище
        """
        movie = None
        async with self.internal_uow as internal:
            movie = await internal.films.get_film_by_id(movie_id)

        if movie:
            return movie

        async with self.external_uow as external:

            movie = await external.films.get_film_by_id(movie_id)
            if not movie:
                raise MovieNotFoundException(movie_id)

            async with self.db_uow as db:
                create_data = CreateMovie.model_validate(movie.model_dump())
                try:
                    movie = await db.films.create_movie(create_data)
                    print("Фильм создан")
                except NotImplementedError:
                    pass
                return movie
