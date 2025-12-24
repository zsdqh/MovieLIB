from passlib.context import CryptContext

from backend.src.auth.users.domain.interfaces.password_hasher import IPasswordHasher


class PasswordHasher(IPasswordHasher):
    """Реализация интерфейса хеширования пароля с использованием sha256_crypt"""

    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Надежное хеширование пароля"""
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка хеша введенного пароля с хешем другого пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)
