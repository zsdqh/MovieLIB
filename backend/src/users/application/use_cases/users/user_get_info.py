from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.use_cases.users.base import UserUseCase
from backend.src.users.domain.entities import User


class GetUserInfoUseCase(UserUseCase):
    """Получение информации об одном пользователе"""

    async def __call__(self, user_data: TokenUser, username: str) -> User:
        async with self.uow:
            obj = await self.uow.users.get_by_username(username)
        return obj
