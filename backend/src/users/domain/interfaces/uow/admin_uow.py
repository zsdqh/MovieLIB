import abc

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.users.domain.interfaces.repository.admin_repo import IAdminRepository


class IAdminUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    admin_work: IAdminRepository
