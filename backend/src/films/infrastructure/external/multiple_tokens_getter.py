import time
from typing import Any

import httpx
from httpx import Response

from backend.src.core.domain.exceptions import DomainException, NotFoundException
from backend.src.films.domain.exceptions import RequestLimitExceededException


class MultipleTokensGetter(httpx.AsyncClient):
    """Класс для отправки get запросов с подставлением разных токенов доступа"""

    def __init__(
        self, base_url: str, tokens: list[str], *args: Any, **kwargs: Any
    ) -> None:
        """Инициализация отправителя запросов со списком заменяемых токенов"""
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.tokens = tokens
        self.current_token = 0

    async def get(self, url: httpx.URL | str, *args: Any, **kwargs: Any) -> Response:
        """
        Каждому запросу присваивается заголовок с токеном для доступа,
        если приходит ошибка о том, что запросы для токена кончились,
        то счетчик увеличивается и используется другой токен
        :raises RequestLimitExceededException: все токены израсходованы
        """
        try:
            self.headers.update({"X-API-KEY": f"{self.tokens[self.current_token]}"})
            start = time.time()
            res = await super().get(str(self.base_url) + str(url), *args, **kwargs)
            print(f"{time.time() - start:.2f}c {res.request.url}")
            if res.status_code == 200:
                return res
            if res.status_code == 403:
                raise RequestLimitExceededException()
            if res.status_code == 404:
                raise NotFoundException()
            raise DomainException(detail=res.json())

        except RequestLimitExceededException:
            self.current_token += 1
            if self.current_token >= len(self.tokens):
                raise
            return await self.get(url, *args, **kwargs)
