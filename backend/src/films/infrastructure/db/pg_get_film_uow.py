from typing import Any

from backend.src.films.domain.interfaces.get_film_uow import IGetFilmUnitOfWork
from backend.src.films.infrastructure.db.pg_get_film_repository import (
    PGGetFilmRepository,
)
from backend.src.users.infrastructure.db.units_of_work.pg_uow import PGUnitOfWork


class PGGetFilmUnitOfWork(PGUnitOfWork, IGetFilmUnitOfWork):
    """Реализация единицы работы с пользователями"""

    async def __aenter__(self) -> IGetFilmUnitOfWork:
        """
        Вход в асинхронный контекстный менеджер

        Создает новую сессию и инициализирует репозиторий
        """
        self.session = self.session_factory()

        self.films = PGGetFilmRepository(self.session)

        return await super().__aenter__()

    async def __aexit__(self, *args: Any) -> None:
        try:
            await super().__aexit__(*args)
        except NotImplementedError:
            pass
