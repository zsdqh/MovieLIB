import abc


class IPasswordHasher(abc.ABC):
    """Интерфейс для класса, реализующего хеширование пароля"""

    @abc.abstractmethod
    def hash(self, password: str) -> str:
        """Генерация хеша пароля"""

    @abc.abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнение пароля с захешированной строкой"""
