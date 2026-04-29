import abc

from pydantic import ValidationError

from backend.src.films.domain.entities.crud import CreateMovie
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.exceptions import NotEnoughDataException
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork
from backend.src.films.domain.interfaces.movie_uow import IMovieUnitOfWork


class MovieUseCase(abc.ABC):
    """
    Абстрактный базовый класс, реализующий внедрение базовых зависимостей,
    которые нужны в каждом варианте использования
    """

    def __init__(
        self,
        external_get_movies_uow: IGetMovieUnitOfWork,
        internal_get_movies_uow: IGetMovieUnitOfWork,
        db_uow: IMovieUnitOfWork,
    ) -> None:
        """Получение зависимостей для работы с фильмами"""
        self.external_uow = external_get_movies_uow
        self.internal_uow = internal_get_movies_uow
        self.db_uow = db_uow

    async def create_movie(self, movie_data: Movie, refresh: bool = False) -> Movie:
        """Функция создания фильма в БД из доменной сущности"""
        async with self.db_uow as db:
            try:
                create_data = CreateMovie.model_validate(
                    {
                        **movie_data.model_dump(),
                        "kp_rating": movie_data.rating.kp_rating,
                    }
                )
            except ValidationError as e:
                raise NotEnoughDataException() from e
            movie = await db.films.create_movie(create_data, refresh=refresh)
            return movie
