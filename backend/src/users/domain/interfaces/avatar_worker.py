import abc
import uuid


class IAvatarWorker(abc.ABC):
    """Класс для работы с файлами"""

    @abc.abstractmethod
    async def save_avatar(self, file: bytes, person_id: uuid.UUID) -> str:
        """Сохранение файла и возвращение ссылки на него"""

    @abc.abstractmethod
    async def delete_avatar(self, file_url: str) -> None:
        """Удаление файла"""
