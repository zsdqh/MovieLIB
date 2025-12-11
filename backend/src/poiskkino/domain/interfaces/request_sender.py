from abc import ABC, abstractmethod

import httpx


class IRequestSender(ABC):
    """Интерфейс отправки запросов к сторонним api"""

    base_url: str

    @abstractmethod
    async def get(
        self, url: str, params: dict[str, str], headers: dict[str, str]
    ) -> httpx.Response:
        """Отправка GET запроса к стороннему api"""
