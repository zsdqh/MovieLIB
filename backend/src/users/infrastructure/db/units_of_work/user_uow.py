from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork
from backend.src.users.infrastructure.db.repositories.user_repository import (
    PGUserRepository,
)


class PGUserUnitOfWork(PGUnitOfWork, IUserUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.users = PGUserRepository(self.session)

        return await super().__aenter__()
