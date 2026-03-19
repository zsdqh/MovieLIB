from pydantic import ValidationError

from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.dtos import UserRegisterDTO
from backend.src.users.domain.entities import User, UserRegister
from backend.src.users.domain.exceptions import ValidationCustomException
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class UserRegisterUseCase(UserUseCase):
    """Регистрация нового пользователя"""

    def __init__(self, uow: IUserUnitOfWork, pwd_hasher: IPasswordHasher):
        self.pwd_hasher = pwd_hasher
        super().__init__(uow)

    async def __call__(
        self,
        user_data: UserRegisterDTO,
    ) -> User:
        try:
            usr = UserRegister(
                **user_data.model_dump(exclude={"password"}),
                hashed_password=self.pwd_hasher.hash(user_data.password),
            )
        except ValidationError as e:
            raise ValidationCustomException(e) from e
        async with self.uow:
            new_user = await self.uow.users.add(usr)
        return new_user
