from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase


class RemoveAvatarUseCase(UserUseCase):
    """Удаление аватара пользователя"""

    async def __call__(self, user: TokenUser) -> str | None:
        async with self.uow:
            return await self.uow.users.remove_avatar(user.sub)
