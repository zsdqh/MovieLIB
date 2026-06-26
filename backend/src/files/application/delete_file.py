from backend.src.files.application.base import FileUseCase


class DeleteFileUseCase(FileUseCase):
    """Удаление файла"""

    async def __call__(self, link: str, is_avatar: bool) -> None:
        filename = self.storage.get_name_from_link(link, True)
        return await self.storage.delete_file(filename, is_avatar)
