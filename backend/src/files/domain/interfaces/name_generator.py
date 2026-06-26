import abc
import uuid


class INameGenerator(abc.ABC):
    """Интерфейс генератора названий файлов"""

    @abc.abstractmethod
    def generate_avatar_name(self, user_id: uuid.UUID) -> str:
        """Создание имени файла для аватара пользователя"""

    @abc.abstractmethod
    def generate_person_name(self, person_id: int) -> str:
        """Создание имени файла для фото участника съемочной группы"""

    @abc.abstractmethod
    def generate_poster_name(self, movie_id: int) -> str:
        """Создание имени файла для постера фильма"""

    @abc.abstractmethod
    def generate_backdrop_name(self, movie_id: int) -> str:
        """Создание имени файла для фона фильма"""
