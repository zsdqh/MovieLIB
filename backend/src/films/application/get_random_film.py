from backend.src.films.application.movie_use_case import MovieUseCase
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import RandomParams


class GetRandomFilmUseCase(MovieUseCase):
    """Получение случайного фильма по заданным параметрам"""

    async def __call__(self, rand_params: RandomParams) -> Movie | None:
        async with self.external_uow:
            movie = await self.external_uow.films.get_random_film(rand_params)

            if not movie:
                return None
            return await self.create_movie(movie)
