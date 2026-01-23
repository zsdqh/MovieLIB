from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.use_cases.users.base import UserUseCase


class DeleteUserProfileUseCase(UserUseCase):
    """Удаление аккаунта пользователя"""

    async def __call__(self, user_data: TokenUser) -> None:
        async with self.uow:
            await self.uow.users.delete(user_data.sub)
