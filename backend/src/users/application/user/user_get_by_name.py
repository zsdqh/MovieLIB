from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.entities import User


class GetUserByNameUseCase(UserUseCase):
    """Получение информации об одном пользователе по имени"""

    async def __call__(self, username: str) -> User:
        async with self.uow:
            obj = await self.uow.users.get_by_username(username)
        return obj
