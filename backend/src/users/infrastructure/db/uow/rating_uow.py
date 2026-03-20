from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.users.domain.interfaces.uow.rating_uow import IRatingUnitOfWork
from backend.src.users.infrastructure.db.repositories.rating_repository import (
    PGRatingRepository,
)


class PGRatingUnitOfWork(PGUnitOfWork, IRatingUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.ratings = PGRatingRepository(self.session)

        return await super().__aenter__()
