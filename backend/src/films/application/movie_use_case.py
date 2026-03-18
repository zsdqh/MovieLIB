import abc

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
