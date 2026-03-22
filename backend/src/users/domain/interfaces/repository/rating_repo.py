import abc
import uuid


class IRatingRepository(abc.ABC):
    """Репозиторий для работы с внутренними рейтингами фильмов"""

    @abc.abstractmethod
    async def set_rate(self, user_id: uuid.UUID, movie_id: int, rating: int) -> None:
        """Установка оценки фильма пользователем"""

    @abc.abstractmethod
    async def remove_rate(self, user_id: uuid.UUID, movie_id: int) -> None:
        """Удаление оценки фильма пользователем"""

    @abc.abstractmethod
    async def get_user_rating(self, user_id: uuid.UUID, movie_id: int) -> int | None:
        """Текущая оценка пользователя фильму или None"""
