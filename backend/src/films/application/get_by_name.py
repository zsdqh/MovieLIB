from backend.src.films.application.movie_use_case import MovieUseCase
from backend.src.films.domain.entities.entities import Movie


class GetMoviesByNameUseCase(MovieUseCase):
    """Получение фильмов по названию"""

    async def __call__(self, query: str, page: int) -> list[Movie]:
        async with self.external_uow:
            return await self.external_uow.films.get_films_by_name(query, page)
