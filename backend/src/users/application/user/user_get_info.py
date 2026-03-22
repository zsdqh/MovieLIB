import uuid

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.entities import User


class GetUserInfoUseCase(UserUseCase):
    """Получение информации об одном пользователе"""

    async def __call__(self, user_data: TokenUser, user_id: uuid.UUID) -> User:
        async with self.uow:
            obj = await self.uow.users.get_by_id(user_id)
        return obj
