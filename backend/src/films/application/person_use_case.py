import abc

from backend.src.films.domain.interfaces.get_person_uow import IGetPersonUnitOfWork
from backend.src.films.domain.interfaces.movie_uow import IMovieUnitOfWork


class PersonUseCase(abc.ABC):
    """
    Абстрактный базовый класс, реализующий внедрение базовых зависимостей,
    которые нужны в каждом варианте использования
    """

    def __init__(
        self,
        external_get_persons_uow: IGetPersonUnitOfWork,
        internal_get_persons_uow: IGetPersonUnitOfWork,
        db_uow: IMovieUnitOfWork,
    ) -> None:
        """Получение зависимостей для работы с фильмами"""
        self.external_uow = external_get_persons_uow
        self.internal_uow = internal_get_persons_uow
        self.db_uow = db_uow
