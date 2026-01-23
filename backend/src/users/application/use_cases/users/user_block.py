from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.use_cases.users.base import UserUseCase
from backend.src.users.domain.entities import User


class UserBlockUseCase(UserUseCase):
    """Изменение блокировки пользователя"""

    async def __call__(
        self, username: str, new_status: bool, user_data: TokenUser
    ) -> User:
        """Изменение статуса по имени"""
        check_admin_only(user_data)
        async with self.uow:
            res = await self.uow.users.change_block_status(username, new_status)
        return res
