import uuid

from backend.src.auth.users.domain.interfaces.avatar_worker import IAvatarWorker


class AvatarWorker(IAvatarWorker):
    """Реализация интерфейса работника с аватарами пользователей"""

    async def save_avatar(self, file: bytes, person_id: uuid.UUID) -> str:
        raise NotImplementedError()

    async def delete_avatar(self, file_url: str) -> None:
        raise NotImplementedError()
