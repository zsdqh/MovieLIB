from typing import Any

from backend.src.files.application.upload_file import UploadFileUseCase


class UploadPosterUseCase(UploadFileUseCase):
    """Загрузка постера в хранилище"""

    async def __call__(self, file: Any, film_id: int) -> str:
        filename = self.name_generator.generate_poster_name(film_id)
        await self.storage.store_file(filename, file, False)
        return self.storage.get_link(filename, False)
