from abc import ABC, abstractmethod
from typing import Any


class IRequestSender(ABC):
    """Интерфейс отправки запросов к сторонним api"""

    base_url: str

    @abstractmethod
    async def get(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        """Отправка GET запроса к стороннему api"""
