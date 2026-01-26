from backend.src.films.domain.interfaces.film_uow import IFilmUnitOfWork
from backend.src.films.infrastructure.db.pg_film_repository import PGFilmRepository
from backend.src.users.infrastructure.db.units_of_work.pg_uow import PGUnitOfWork


class PGFilmUnitOfWork(PGUnitOfWork, IFilmUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IFilmUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.films = PGFilmRepository(self.session)

        return await super().__aenter__()
