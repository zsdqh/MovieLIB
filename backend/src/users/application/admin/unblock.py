from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.admin.base import AdminUseCase


class UnblockUserUseCase(AdminUseCase):
    """Удаление одной блокировки пользователя"""

    async def __call__(self, blocking_id: int, user_data: TokenUser) -> None:
        check_admin_only(user_data)
        async with self.uow:
            await self.uow.admin_work.unblock_user(blocking_id)
