from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.users.application.use_cases.users.base import UserUseCase
from backend.src.auth.users.domain.entities import User
from backend.src.auth.users.domain.interfaces.avatar_worker import IAvatarWorker
from backend.src.auth.users.domain.interfaces.user_uow import IUserUnitOfWork


class RemoveAvatarUseCase(UserUseCase):
    """Удаление аватара пользователя"""

    def __init__(self, uow: IUserUnitOfWork, file_worker: IAvatarWorker) -> None:
        self.file_worker = file_worker
        super().__init__(uow)

    async def __call__(self, user: TokenUser) -> User:
        await self.file_worker.delete_avatar(user.avatar_url)
        async with self.uow:
            return await self.uow.users.remove_avatar(user.sub)
