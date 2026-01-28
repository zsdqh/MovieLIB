from typing import Any

from backend.src.files.application.upload_file import UploadFileUseCase


class UploadBackdropUseCase(UploadFileUseCase):
    """Загрузка фона фильма в хранилище"""

    async def __call__(self, file: Any, film_id: int) -> str:
        filename = self.name_generator.generate_backdrop_name(film_id)
        await self.storage.store_file(filename, file, False)
        return self.storage.get_link(filename, is_avatar=False)
