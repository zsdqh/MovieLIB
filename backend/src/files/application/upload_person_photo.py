from typing import Any

from backend.src.files.application.upload_file import UploadFileUseCase


class UploadPersonPhotoUseCase(UploadFileUseCase):
    """Загрузка фото персоны в хранилище"""

    async def __call__(self, file: Any, person_id: int) -> str:
        filename = self.name_generator.generate_person_name(person_id)
        await self.storage.store_file(filename, file, False)
        return self.storage.get_link(filename, False)
