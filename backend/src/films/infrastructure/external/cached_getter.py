from typing import Any, Optional

import httpx
import redis.asyncio as redis
from httpx import Response
from pydantic import BaseModel


class ResponseDTO(BaseModel):
    """Модель для работы с запросом в кешее"""

    status_code: int
    headers: dict[str, Any]
    body: bytes
    url: str


class CachedGetter(httpx.AsyncClient):
    """Клиент, кеширующий GET запросы в redis"""

    def __init__(
        self,
        redis_client: redis.Redis,
        *args: Any,
        cache_ttl: int = 60 * 30,
        cache_prefix: str = "api_cache",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.redis = redis_client
        self.cache_ttl = cache_ttl
        self.cache_prefix = cache_prefix

    async def get(
        self,
        url: httpx.URL | str,
        *args: Any,
        to_cache: bool = True,
        **kwargs: Any,
    ) -> Response:
        cache_key = f"{self.cache_prefix}:{url}:{kwargs.get("params")}"
        cached = await self._get_from_cache(cache_key)
        if cached is not None:
            print("Cache hit!")
            return cached

        response = await super().get(url, *args, **kwargs)

        if to_cache and response.status_code in (200, 404):
            await self._save_to_cache(cache_key, response)

        return response

    async def _get_from_cache(self, key: str) -> Optional[Response]:
        """Восстановить Response из Redis, если ключ существует"""
        try:
            data = await self.redis.get(key)
            if data is None:
                return None
            cached = ResponseDTO.model_validate_json(data)
            return Response(
                status_code=cached.status_code,
                headers=cached.headers,
                content=cached.body,
                request=httpx.Request("GET", cached.url),
            )
        except Exception as e:
            print(f"Ошибка чтения из redis: {e}")
            return None

    async def _save_to_cache(self, key: str, response: Response) -> None:
        """Сохранить ответ в Redis с TTL"""
        try:
            headers = dict(response.headers)
            headers.pop("content-encoding", None)
            # сайты могут отсылать content-encoding и НЕ КОДИРОВАТЬ данные
            # просто убираем content-encoding и все работает
            payload = ResponseDTO.model_validate(
                {
                    "status_code": response.status_code,
                    "headers": headers,
                    "body": response.content,
                    "url": str(response.url),
                }
            )
            await self.redis.set(
                name=key,
                ex=self.cache_ttl,
                value=payload.model_dump_json(ensure_ascii=True),
            )
        except Exception as e:
            print(f"Ошибка записи в redis: {e}")
