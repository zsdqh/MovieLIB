import uuid

from backend.src.files.domain.interfaces.name_generator import INameGenerator


class NameGenerator(INameGenerator):
    """Реализация интерфейса генератора названий файлов"""

    def generate_person_name(self, person_id: int) -> str:
        """
        Генерация имени для хранения фото человека
        """
        return self._generate_name("person", person_id)

    def generate_poster_name(self, movie_id: int) -> str:
        """
        Генерация имени для хранения постера фильма
        """
        return self._generate_name("poster", movie_id)

    def generate_backdrop_name(self, movie_id: int) -> str:
        """
        Генерация имени для хранения фона фильма
        """
        return self._generate_name("backdrop", movie_id)

    def generate_avatar_name(self, user_id: uuid.UUID) -> str:
        """
        Генерация имени для хранения аватарки
        """
        return self._generate_name("avatar", user_id)

    def _generate_name(self, prefix: str, obj_id: int | uuid.UUID) -> str:
        """Генерация имени из префикса и id объекта"""
        return f"{prefix}_{obj_id}"
