from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.films.domain.interfaces.movie_uow import IMovieUnitOfWork
from backend.src.films.infrastructure.db.pg_movie_repository import PGMovieRepository


class PGMovieUnitOfWork(PGUnitOfWork, IMovieUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IMovieUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.films = PGMovieRepository(self.session)

        return await super().__aenter__()
