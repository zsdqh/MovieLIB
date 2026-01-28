import abc
from typing import Any


class IS3Worker(abc.ABC):
    """Интерфейс для работы с S3 совместимым хранилищем"""

    @abc.abstractmethod
    async def store_file(
        self, filename: str, file_data: Any, is_avatar: bool = False
    ) -> None:
        """Помещение файла в хранилище"""

    @abc.abstractmethod
    async def delete_file(self, filename: str, is_avatar: bool = False) -> None:
        """Удаление файла"""

    @abc.abstractmethod
    def get_link(self, filename: str, is_avatar: bool) -> str:
        """Получение ссылки на публичный объект"""

    @abc.abstractmethod
    def get_name_from_link(self, url: str, is_avatar: bool) -> str:
        """Получение имени файла из ссылки на публичный объект"""
