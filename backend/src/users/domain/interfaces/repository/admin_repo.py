import abc
from datetime import date
from typing import Iterable

from backend.src.users.domain.dtos import ListOfUsersParams
from backend.src.users.domain.entities import (
    BlockingWithUser,
    CreateBlocking,
    Report,
    User,
)


class IAdminRepository(abc.ABC):
    """
    Интерфейс для администраторского репозитория
    Определяет взаимодействия с таблицей пользователей
    """

    @abc.abstractmethod
    async def user_list(self, params: ListOfUsersParams) -> Iterable[User]:
        """
        Получение списка пользователей, соответствующего условиям
        :param params: условия, которым должна удовлетворять выборка
        """

    @abc.abstractmethod
    async def block_user(self, create_data: CreateBlocking) -> BlockingWithUser:
        """Блокировка пользователя с указанием причины"""

    @abc.abstractmethod
    async def unblock_user(self, blocking_id: int) -> None:
        """Удаление блокировки пользователя"""

    @abc.abstractmethod
    async def get_reports(self, start_from: date | None) -> list[Report]:
        """Получение всех жалоб, начиная с определенной даты"""

    @abc.abstractmethod
    async def change_comment_policy(self, new_text: str) -> None:
        """Изменение правил написания комментариев"""

    @abc.abstractmethod
    async def solve_report(self, report_id: int) -> Report:
        """Отметка того, что жалоба была рассмотрена"""
