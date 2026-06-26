from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork


class GetSimilarUseCase:
    """Получение похожих фильмов"""

    def __init__(
        self,
        external_movie_uow: IGetMovieUnitOfWork,
        internal_movie_uow: IGetMovieUnitOfWork,
    ):
        """Получение единицы работы получения фильмов"""
        self.external_uow = external_movie_uow
        self.internal_uow = internal_movie_uow

    async def __call__(self, movie_id: int) -> list[Movie]:
        async with self.external_uow:
            res = await self.external_uow.films.get_similar_films(movie_id)
        if not res:
            print("Получение похожих фильмов из БД, менее точно")
            async with self.internal_uow:
                res = await self.internal_uow.films.get_similar_films(movie_id)
        return res
