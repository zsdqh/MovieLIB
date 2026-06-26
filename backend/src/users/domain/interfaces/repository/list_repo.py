import abc

from backend.src.users.domain.entities import (
    CreateList,
    DeleteList,
    EditList,
    ListMovie,
    UserList,
)


class IListRepository(abc.ABC):
    """Репозиторий для работы с пользовательскими списками фильмов"""

    @abc.abstractmethod
    async def create_list(self, list_data: CreateList) -> UserList:
        """Создание пользовательского списка"""

    @abc.abstractmethod
    async def edit_list(self, update_data: EditList) -> UserList:
        """Изменение данных о пользовательском списке"""

    @abc.abstractmethod
    async def delete_list(self, delete_data: DeleteList) -> None:
        """Удаление пользовательского списка"""

    @abc.abstractmethod
    async def add_movie(self, add_data: ListMovie) -> UserList:
        """Добавление фильма в пользовательский список"""

    @abc.abstractmethod
    async def remove_movie(self, remove_data: ListMovie) -> UserList:
        """Удаление фильма из пользовательского списка"""
