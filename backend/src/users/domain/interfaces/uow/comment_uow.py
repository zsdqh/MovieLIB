import abc

from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.users.domain.interfaces.repository.comment_repository import (
    ICommentRepository,
)


class ICommentUnitOfWork(IUnitOfWork, abc.ABC):
    """Интерфейс единицы работы с комментариями"""

    comments: ICommentRepository
