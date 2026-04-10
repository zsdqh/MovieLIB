from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.users.domain.interfaces.uow.admin_uow import IAdminUnitOfWork
from backend.src.users.infrastructure.db.repositories.admin_repository import (
    PGAdminRepository,
)


class PGAdminUnitOfWork(PGUnitOfWork, IAdminUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.admin_work = PGAdminRepository(self.session)

        return await super().__aenter__()
