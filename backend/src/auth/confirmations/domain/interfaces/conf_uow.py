import abc

from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.db.domain.interfaces.uow import IUnitOfWork


class IConfUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    confirmations: IConfRepository
