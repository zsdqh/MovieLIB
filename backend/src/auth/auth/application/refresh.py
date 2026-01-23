from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.interfaces.token_auth import ITokenAuth
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class RefreshUseCase:
    """Обновление токенов"""

    def __init__(self, token_worker: ITokenAuth, uow: IUserUnitOfWork):
        """Внедрение зависимости для работы с токенами"""
        self.uow = uow
        self.token_worker = token_worker

    async def __call__(self, user_data: TokenUser) -> User:
        """
        Выдача новой пары токенов refresh и access с
        изменением номера валидного refresh токена у пользователя
        и обновлением информации о пользователе
        """
        async with self.uow:
            obj = await self.uow.users.get_by_id(user_data.sub)
            user_data = TokenUser.model_validate(obj.model_dump())
            self.token_worker.refresh_tokens(user_data)
            obj = await self.uow.users.update(
                UserUpdate(valid_refresh_id=obj.valid_refresh_id + 1, id=user_data.sub)
            )
            return obj
