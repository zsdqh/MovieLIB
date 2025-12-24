import abc
from typing import Any


class IUnitOfWork(abc.ABC):
    """
    Интерфейс единицы работы, определяющий рамки транзакций
    """

    @abc.abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Вход в контекст единицы работы"""

    @abc.abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        """
        Выход из контекста единицы работы, откатывающий незафиксированные изменения
        """
