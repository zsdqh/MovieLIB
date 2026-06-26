from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.users.domain.interfaces.uow.list_uow import IListUnitOfWork
from backend.src.users.infrastructure.db.repositories.list_repository import (
    PGListRepository,
)


class PGListUnitOfWork(PGUnitOfWork, IListUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.lists = PGListRepository(self.session)

        return await super().__aenter__()
