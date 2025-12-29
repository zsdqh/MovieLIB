from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.users.application.use_cases.users.base import UserUseCase
from backend.src.auth.users.domain.entities import User


class GetUserInfoUseCase(UserUseCase):
    """Получение информации об одном пользователе"""

    async def __call__(self, user_data: TokenUser, username: str) -> User:
        check_admin_only(user_data)
        async with self.uow:
            obj = await self.uow.users.get_by_username(username)
        return obj
