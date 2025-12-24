import abc
from typing import Any

from backend.src.auth.auth.domain.entities import TokenUser


class ITokenProvider(abc.ABC):
    """Интерфейс генератора токенов"""

    @abc.abstractmethod
    def create_access_token(self, data: dict[str, Any]) -> str:
        """Создание access токена"""

    @abc.abstractmethod
    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Создание refresh токена"""

    @abc.abstractmethod
    def read_token(self, token: str) -> TokenUser:
        """Получение данных из токена"""
