from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork
from backend.src.films.infrastructure.db.pg_get_film_repository import (
    PGGetMovieRepository,
)


class PGGetMovieUnitOfWork(PGUnitOfWork, IGetMovieUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IGetMovieUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.films = PGGetMovieRepository(self.session)

        return await super().__aenter__()
