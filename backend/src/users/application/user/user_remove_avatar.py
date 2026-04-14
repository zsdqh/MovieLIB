import uuid

from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase


class RemoveAvatarUseCase(UserUseCase):
    """Удаление аватара пользователя"""

    async def __call__(
        self, user: TokenUser, user_id: uuid.UUID | None = None
    ) -> str | None:
        async with self.uow:
            if not user_id:
                return await self.uow.users.remove_avatar(user.sub)
            check_admin_only(user)
            return await self.uow.users.remove_avatar(user_id)
