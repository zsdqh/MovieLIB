import abc

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.users.domain.interfaces.repository.rating_repo import IRatingRepository


class IRatingUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с пользователями"""

    ratings: IRatingRepository
