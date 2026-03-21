from backend.src.db.domain.interfaces.uow import IUnitOfWork
from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.users.domain.interfaces.uow.comment_uow import ICommentUnitOfWork
from backend.src.users.infrastructure.db.repositories.comment_repository import (
    PGCommentRepository,
)


class PGCommentUnitOfWork(PGUnitOfWork, ICommentUnitOfWork):
    """Реализация единицы работы с комментарими"""

    async def __aenter__(self) -> IUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.comments = PGCommentRepository(self.session)

        return await super().__aenter__()
