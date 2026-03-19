from typing import Iterable

from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.dtos import ListParams
from backend.src.users.domain.entities import User


class UserListUseCase(UserUseCase):
    """Список пользователей с фильтрацией, сортировкой и пагинацией"""

    async def __call__(
        self, list_conditions: ListParams, user_data: TokenUser
    ) -> Iterable[User]:
        """
        Доступно только для пользователей с разрешением на чтение

        :param list_conditions: условия фильтрации/сортировки
        :return: список, удовлетворяющий условиям
        """
        check_admin_only(user_data)

        async with self.uow:
            users = await self.uow.users.list(list_conditions)
            return users
