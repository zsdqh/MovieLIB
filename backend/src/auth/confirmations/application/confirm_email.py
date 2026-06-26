from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.confirmations.domain.exceptions import WrongCodeException
from backend.src.auth.confirmations.domain.interfaces.conf_uow import IConfUnitOfWork
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork


class ConfirmEmailUseCase:
    """Подвтверждение почты пользователя"""

    def __init__(self, conf_uow: IConfUnitOfWork, user_uow: IUserUnitOfWork):
        """Единицы работы для пользователя и подтверждения"""
        self.conf_uow = conf_uow
        self.user_uow = user_uow

    async def __call__(self, user_data: TokenUser, code: str) -> User:
        """Сравнение переданного кода и хранимого кода подтверждения почты"""
        async with self.conf_uow:
            conf_obj = await self.conf_uow.confirmations.get_by_user_id(
                user_id=user_data.sub
            )

        if conf_obj.token != code:
            raise WrongCodeException("Неправильный код подтверждения")

        async with self.user_uow:
            user_obj = await self.user_uow.users.update(
                update_data=UserUpdate(id=user_data.sub, is_activated=True)
            )

        return user_obj
