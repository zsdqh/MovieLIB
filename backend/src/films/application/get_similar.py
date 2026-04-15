from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork


class GetSimilarUseCase:
    """Получение похожих фильмов"""

    def __init__(self, get_movie_uow: IGetMovieUnitOfWork):
        """Получение единицы работы получения фильмов"""
        self.uow = get_movie_uow

    async def __call__(self, movie_id: int) -> list[Movie]:
        async with self.uow:
            return await self.uow.films.get_similar_films(movie_id)
