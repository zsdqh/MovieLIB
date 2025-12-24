from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.interfaces.token_auth import ITokenAuth
from backend.src.auth.users.domain.entities import UserUpdate
from backend.src.auth.users.domain.interfaces.user_uow import IUserUnitOfWork


class LogoutUseCase:
    """Выход пользователя из аккаунта"""

    def __init__(
        self,
        uow: IUserUnitOfWork,
        token_worker: ITokenAuth,
    ):
        """Внедрение зависимостей для работы с токенами и БД"""
        self.uow = uow
        self.token_worker = token_worker

    async def __call__(self, user_data: TokenUser) -> None:
        """Удаление токенов"""
        self.token_worker.unset_tokens()
        async with self.uow:
            # Инвалидируем refresh токен
            await self.uow.users.update(
                UserUpdate(
                    valid_refresh_id=user_data.valid_refresh_id + 1, id=user_data.sub
                )
            )
