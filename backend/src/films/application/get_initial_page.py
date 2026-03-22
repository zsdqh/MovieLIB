from backend.src.films.application.movie_use_case import MovieUseCase
from backend.src.films.domain.entities.entities import Movie


class GetInitialPageUseCase(MovieUseCase):
    """Загрузка начальной страницы"""

    async def __call__(self, page: int) -> list[Movie]:
        async with self.external_uow:
            return await self.external_uow.films.get_random_films(page)
