from backend.src.db.infrastructure.pg_uow import PGUnitOfWork
from backend.src.films.domain.interfaces.get_person_uow import IGetPersonUnitOfWork
from backend.src.films.infrastructure.db.pg_get_person_repository import (
    PGGetPersonRepository,
)


class PGGetPersonUnitOfWork(PGUnitOfWork, IGetPersonUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IGetPersonUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.persons = PGGetPersonRepository(self.session)

        return await super().__aenter__()
