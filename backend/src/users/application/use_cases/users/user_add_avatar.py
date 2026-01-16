from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.use_cases.users.base import UserUseCase
from backend.src.users.domain.entities import User, UserUpdate
from backend.src.users.domain.interfaces.avatar_worker import IAvatarWorker
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class AddAvatarUseCase(UserUseCase):
    """Добавление аватара пользователя"""

    def __init__(self, uow: IUserUnitOfWork, file_worker: IAvatarWorker) -> None:
        self.file_worker = file_worker
        super().__init__(uow)

    async def __call__(self, user: TokenUser, avatar: bytes) -> User:
        avatar_url = await self.file_worker.save_avatar(avatar, user.sub)
        async with self.uow:
            return await self.uow.users.update(
                UserUpdate(id=user.sub, avatar_url=avatar_url)
            )
