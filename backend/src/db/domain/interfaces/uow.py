import abc
from typing import Any


class IUnitOfWork(abc.ABC):
    """
    Интерфейс единицы работы, определяющий рамки транзакций
    """

    async def __aenter__(self) -> "IUnitOfWork":
        """Вход в контекст единицы работы"""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """
        Выход из контекста единицы работы, откатывающий незафиксированные изменения
        """
        await self.rollback()

    async def commit(self) -> None:
        """Фиксация изменений внутри единицы работы"""
        await self._commit()

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Откат незафиксированных изменений"""

    @abc.abstractmethod
    async def _commit(self) -> None:
        """Внутренняя реализация фиксации изменений"""
