from backend.src.auth.users.domain.interfaces.uow import IUnitOfWork
from backend.src.auth.users.domain.interfaces.user_uow import IUserUnitOfWork
from backend.src.auth.users.infrastructure.db.repositories.user_repository import (
    PGUserRepository,
)
from backend.src.auth.users.infrastructure.db.units_of_work.pg_uow import PGUnitOfWork


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
