import datetime

from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.admin.base import AdminUseCase
from backend.src.users.domain.entities import Blocking, CreateBlocking


class BlockUserUseCase(AdminUseCase):
    """Изменение блокировки пользователя"""

    async def __call__(
        self, create_data: CreateBlocking, user_data: TokenUser
    ) -> Blocking:
        """Изменение статуса по имени"""
        check_admin_only(user_data)
        if create_data.ends_at:
            create_data.ends_at = create_data.ends_at.astimezone(
                datetime.timezone.utc
            ).replace(tzinfo=None)
        async with self.uow:
            res = await self.uow.admin_work.block_user(create_data)
        return res
