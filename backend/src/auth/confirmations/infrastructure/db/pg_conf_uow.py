from backend.src.auth.confirmations.domain.interfaces.conf_uow import IConfUnitOfWork
from backend.src.auth.confirmations.infrastructure.db.pg_conf_repository import (
    PGConfRepository,
)
from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork


class PGConfUnitOfWork(PGUnitOfWork, IConfUnitOfWork):
    """Реализация единицы работы с подтверждениями"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.confirmations = PGConfRepository(self.session)

        return await super().__aenter__()
