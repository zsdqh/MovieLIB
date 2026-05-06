from backend.src.auth.auth.domain.dtos import LoginDTO
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.interfaces.token_auth import ITokenAuth
from backend.src.core.domain.exceptions import UnauthorizedException
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork


class LoginUseCase:
    """Вход пользователя в аккаунт"""

    def __init__(
        self,
        uow: IUserUnitOfWork,
        token_worker: ITokenAuth,
        pwd_hasher: IPasswordHasher,
    ):
        """Внедрение зависимостей для работы с токенами, БД и паролем"""
        self.uow = uow
        self.token_worker = token_worker
        self.pwd_hasher = pwd_hasher

    async def __call__(self, login_data: LoginDTO) -> User:
        """Установка access и refresh токенов при правильных входных данных"""
        async with self.uow:
            user = await self.uow.users.get_by_username(login_data.username)

            if not self.pwd_hasher.verify(login_data.password, user.hashed_password):
                raise UnauthorizedException(detail="Неверный пароль")
            user = await self.uow.users.update(
                UserUpdate(id=user.id, valid_refresh_id=user.valid_refresh_id + 1)
            )
            token_data = TokenUser.model_validate(
                {**user.model_dump(), "is_blocked": bool(user.active_blockings)}
            )

            self.token_worker.set_tokens(token_data)

            return user
