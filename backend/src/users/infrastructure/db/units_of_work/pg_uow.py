from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.src.users.domain.interfaces.uow import IUnitOfWork


class PGUnitOfWork(IUnitOfWork):
    """
    Postgres реализация единицы работы для работы с таблицей User

    Управляет сессией и предоставляет доступ к таблице пользователей
    """

    session: AsyncSession
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Создание единицы работы с передачей фабрики создания сессий

        :param session_factory: фабрика сессий
        """
        self.session_factory = session_factory

    async def __aexit__(self, *args: Any) -> None:
        """
        Выход из асинхронного контекстного менеджера

        Откатывает незафиксированные действия внутри сессии
        """
        try:
            await self.commit()
        except SQLAlchemyError:
            pass
        await super().__aexit__(*args)

        await self.session.close()

    async def _commit(self) -> None:
        """
        Фиксирование произведенных в сессии действий
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Откат незафиксированных действий в сессии
        """
        await self.session.rollback()
