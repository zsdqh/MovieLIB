import abc
import uuid
from typing import Iterable
from uuid import UUID

from backend.src.users.domain.dtos import ListParams
from backend.src.users.domain.entities import User, UserRegister, UserUpdate


class IUserRepository(abc.ABC):
    """
    Интерфейс для пользовательского репозитория
    Определяет взаимодействия с таблицей пользователей
    """

    @abc.abstractmethod
    async def add(self, user: UserRegister) -> User:
        """
        Добавление нового пользователя в базу

        :param user: схема с данными для регистрации пользователя
        :return: созданный пользователь
        """

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User:
        """Получение пользователя по имени"""

    @abc.abstractmethod
    async def get_by_id(self, user_id: UUID) -> User:
        """Получение пользователя по id"""

    @abc.abstractmethod
    async def update(self, update_data: UserUpdate) -> User:
        """Обновление информации о пользователе"""

    @abc.abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None:
        """Удаление пользователя по id"""

    @abc.abstractmethod
    async def list(self, params: ListParams) -> Iterable[User]:
        """
        Получение списка пользователей, соответствующего условиям
        :param params: условия, которым должна удовлетворять выборка
        """

    @abc.abstractmethod
    async def change_block_status(self, username: str, status: bool) -> User:
        """Изменение статуса блокировки пользователя"""

    @abc.abstractmethod
    async def remove_avatar(self, user_id: uuid.UUID) -> str | None:
        """Удаление аватара пользователя"""
