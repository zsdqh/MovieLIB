import uuid
from typing import Iterable

from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.users.application.use_cases.users.base import UserUseCase


class GetUsersEmails(UserUseCase):
    """Получение почт пользователей"""

    async def __call__(
        self, user_data: TokenUser, user_ids: list[uuid.UUID]
    ) -> Iterable[str]:
        check_admin_only(user_data)
        async with self.uow:
            obj = await self.uow.users.get_users_emails(user_ids)
        return obj
