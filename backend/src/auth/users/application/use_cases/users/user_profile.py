from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.users.application.use_cases.users.base import UserUseCase
from backend.src.auth.users.domain.entities import User


class UserProfileUseCase(UserUseCase):
    """Личный профиль пользователя"""

    async def __call__(self, user_data: TokenUser) -> User:
        """Получение пользователя из токена"""
        async with self.uow:
            res = await self.uow.users.get_by_id(user_data.sub)
            return res
