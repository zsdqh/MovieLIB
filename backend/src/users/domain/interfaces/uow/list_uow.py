import abc

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.users.domain.interfaces.repository.list_repo import IListRepository


class IListUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    lists: IListRepository
