from typing import Any

import httpx

from backend.src.core.domain.exceptions import DomainException
from backend.src.poiskkino.domain.exceptions import RequestLimitExceededException
from backend.src.poiskkino.domain.interfaces.request_sender import IRequestSender


class SenderWithMultipleTokens(IRequestSender):
    """
    Класс, реализующий интерфейс отправителя запросов,
    который при исчерпании лимита запросов одного токена переключается на следующий,
    пока не закончатся токены
    """

    def __init__(self, base_url: str, tokens: list[str]) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        self.base_url = base_url
        self.tokens = tokens
        self.current_token = 0

    async def get(
        self, url: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                client.headers.update(
                    {"X-API-KEY": f"{self.tokens[self.current_token]}"}
                )
                res = await client.get(self.base_url + url, params=params)
                if res.status_code == 200:
                    return dict(res.json())

                if res.status_code == 403:
                    raise RequestLimitExceededException()
                raise DomainException(detail=res.json())

        except RequestLimitExceededException:
            self.current_token += 1
            if self.current_token >= len(self.tokens):
                raise
            return await self.get(url, params)
