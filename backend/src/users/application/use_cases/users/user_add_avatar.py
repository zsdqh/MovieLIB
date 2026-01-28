from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.use_cases.users.base import UserUseCase
from backend.src.users.domain.entities import User, UserUpdate


class AddAvatarUseCase(UserUseCase):
    """Добавление аватара пользователя"""

    async def __call__(self, user: TokenUser, avatar_url: str) -> User:
        async with self.uow:
            return await self.uow.users.update(
                UserUpdate(id=user.sub, avatar_url=avatar_url)
            )
