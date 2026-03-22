from backend.src.films.application.movie_use_case import MovieUseCase
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import FilmParams


class GetFilteredMoviesUseCase(MovieUseCase):
    """Получить фильмы, отфильтрованные по заданным параметрам"""

    async def __call__(self, params: FilmParams, page: int) -> list[Movie]:
        async with self.external_uow:
            return await self.external_uow.films.get_films_with_params(params, page)
