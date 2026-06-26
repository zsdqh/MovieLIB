from sqlalchemy.ext.asyncio import AsyncSession


class PGRepository:
    """Postgres реализация репозитория"""

    def __init__(self, session: AsyncSession) -> None:
        """
        Создание репозитория с передачей сессии

        :param session: Асинхронная SQLAlchemy сессия
        """
        super().__init__()
        self.session = session
