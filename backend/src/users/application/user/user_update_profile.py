from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.dtos import UserUpdateDTO
from backend.src.users.domain.entities import User, UserUpdate


class UpdateUserProfileUseCase(UserUseCase):
    """Изменение своих данных пользователем"""

    async def __call__(self, user_data: TokenUser, update_data: UserUpdateDTO) -> User:
        async with self.uow:
            to_update = UserUpdate(
                id=user_data.sub, email=update_data.email, username=update_data.username
            )
            if update_data.email and update_data.email != user_data.email:
                to_update.is_activated = False

            obj = await self.uow.users.update(update_data=to_update)
            return obj
