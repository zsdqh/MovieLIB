from pydantic import EmailStr

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork


class ConfirmEmailOAuthUseCase:
    """Подтверждение почты через OAuth email, полученный на frontend."""

    def __init__(self, user_uow: IUserUnitOfWork):
        """Получение единицы работы с пользователем извне"""
        self.user_uow = user_uow

    async def __call__(self, user_data: TokenUser, email: EmailStr) -> User:
        async with self.user_uow:
            return await self.user_uow.users.update(
                update_data=UserUpdate(
                    id=user_data.sub,
                    email=str(email),
                    is_activated=True,
                )
            )
