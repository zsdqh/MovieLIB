import abc

from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.users.domain.interfaces.uow import IUnitOfWork


class IConfUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    confirmations: IConfRepository
