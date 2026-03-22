import argparse
import asyncio

from backend.src.core.container import Container
from backend.src.users.application.user.user_register import (
    UserRegisterUseCase,
)
from backend.src.users.domain.dtos import UserRegisterDTO
from backend.src.users.domain.entities import UserUpdate
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.uow.list_uow import IListUnitOfWork
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork


async def create_superuser(
    username: str,
    email: str,
    password: str,
    uow: IUserUnitOfWork,
    pwd_hasher: IPasswordHasher,
    list_uow: IListUnitOfWork,
) -> None:
    """CLI функция создания суперпользователя"""
    async with uow:
        new_user = await UserRegisterUseCase(uow, list_uow, pwd_hasher)(
            UserRegisterDTO(username=username, email=email, password=password), []
        )
        new_user = await uow.users.update(UserUpdate(id=new_user.id, is_admin=True))
        print(f"Суперпользователь {new_user.username} создан")


def main() -> None:
    """Определение консольной команды для создания суперпользователя"""
    parser = argparse.ArgumentParser(description="Создание суперпользователя")
    parser.add_argument("--username", required=True, help="Имя пользователя")
    parser.add_argument("--email", required=True, help="Email")
    parser.add_argument("--password", required=True, help="Пароль")

    container = Container()
    container.wire(modules=[__name__])

    uow = container.user_uow()
    pwd_hasher = container.password_hasher()
    list_uow = container.list_uow()

    args = parser.parse_args()
    asyncio.run(
        create_superuser(
            args.username, args.email, args.password, uow, pwd_hasher, list_uow
        )
    )


if __name__ == "__main__":
    main()
