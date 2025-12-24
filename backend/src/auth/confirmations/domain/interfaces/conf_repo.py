import abc
import uuid

from backend.src.auth.confirmations.domain.entities import (
    ConfCreate,
    Confirmation,
    ConfUpdate,
)


class IConfRepository(abc.ABC):
    """Интерфейс репозитория для работы с подтверждениями"""

    @abc.abstractmethod
    async def create(self, conf_data: ConfCreate) -> Confirmation:
        """Создание подтверждения"""

    @abc.abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Confirmation:
        """Получение подтверждения по id пользователя"""

    @abc.abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None:
        """Удаление подтверждения"""

    @abc.abstractmethod
    async def update(self, conf_new_data: ConfUpdate) -> Confirmation:
        """Обновление подтверждения"""
