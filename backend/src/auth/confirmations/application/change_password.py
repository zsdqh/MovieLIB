from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.confirmations.domain.entities import NewPassword
from backend.src.auth.confirmations.domain.exceptions import WrongCodeException
from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class ChangePasswordUseCase:
    """Изменение пароля"""

    def __init__(
        self,
        cache_repository: IConfRepository,
        uow: IUserUnitOfWork,
        pwd_hasher: IPasswordHasher,
    ):
        """Зависимости для изменения пароля"""
        self.cache_repository = cache_repository
        self.uow = uow
        self.pwd_hasher = pwd_hasher

    async def __call__(
        self, user_data: TokenUser, code: str, new_password: NewPassword
    ) -> User:
        """
        Сравнение полученного кода с кодом из кеша и
        изменение пароля в случае совпадения
        """
        conf_obj = await self.cache_repository.get_by_user_id(user_data.sub)
        if conf_obj.token != code:
            raise WrongCodeException("Неправильный код подтверждения")

        async with self.uow:
            user_obj = await self.uow.users.update(
                update_data=UserUpdate(
                    id=user_data.sub,
                    hashed_password=self.pwd_hasher.hash(
                        password=new_password.password
                    ),
                )
            )

        # удаляем код, чтобы пароль можно было поменять только один раз по одному коду
        await self.cache_repository.delete(user_data.sub)

        return user_obj
