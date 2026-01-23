import abc

from backend.src.users.domain.interfaces.uow import IUnitOfWork
from backend.src.users.domain.interfaces.user_repo import IUserRepository


class IUserUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    users: IUserRepository
