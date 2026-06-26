from pydantic import ValidationError

from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.dtos import UserRegisterDTO
from backend.src.users.domain.entities import CreateList, User, UserRegister
from backend.src.users.domain.exceptions import ValidationCustomException
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.uow.list_uow import IListUnitOfWork
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork


class UserRegisterUseCase(UserUseCase):
    """Регистрация нового пользователя"""

    def __init__(
        self,
        uow: IUserUnitOfWork,
        list_uow: IListUnitOfWork,
        pwd_hasher: IPasswordHasher,
    ):
        self.pwd_hasher = pwd_hasher
        self.list_uow = list_uow
        super().__init__(uow)

    async def __call__(
        self, user_data: UserRegisterDTO, default_lists: list[str]
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

        async with self.list_uow:
            for list_name in default_lists:
                lst = await self.list_uow.lists.create_list(
                    CreateList(user_id=new_user.id, name=list_name, is_public=True)
                )
                new_user.user_lists.append(lst)

        return new_user
