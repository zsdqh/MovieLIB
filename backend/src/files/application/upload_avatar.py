from typing import Any

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.files.application.upload_file import UploadFileUseCase


class UploadAvatarUseCase(UploadFileUseCase):
    """Загрузка аватара в хранилище"""

    async def __call__(self, file: Any, user_data: TokenUser) -> str:
        filename = self.name_generator.generate_avatar_name(user_data.sub)
        await self.storage.store_file(filename, file, True)
        return self.storage.get_link(filename, True)
