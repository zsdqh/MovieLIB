import uuid

import redis.asyncio as redis

from backend.src.auth.confirmations.domain.entities import (
    ConfCreate,
    Confirmation,
    ConfUpdate,
)
from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.core.domain.exceptions import NotFoundException


class RedisConfRepository(IConfRepository):
    """Реализация репозитория для работы с подтверждениями в Redis(для сброса пароля)"""

    def __init__(self, redis_client: redis.Redis, code_ttl: int) -> None:
        """
        :param redis_client: асинхронный клиент для работы с Redis
        :param code_ttl: время жизни кода подтверждения
        """
        self.redis = redis_client
        self.code_ttl = code_ttl

    async def create(self, conf_data: ConfCreate) -> Confirmation:
        """Создание в кеше подтверждения для сброса пароля"""
        key = self._key_name(conf_data.user_id)
        conf_to_create = Confirmation.model_validate(
            {**conf_data.model_dump(), "id": key}
        )
        await self.redis.set(
            name=key, ex=self.code_ttl, value=conf_to_create.model_dump_json()
        )
        return conf_to_create

    async def get_by_user_id(self, user_id: uuid.UUID) -> Confirmation:
        """Получение подтверждения из кеша"""
        key = self._key_name(user_id)
        obj = await self.redis.get(key)
        if not obj:
            raise NotFoundException(
                "Code to change password not found, try /send_password_confirmation"
            )
        return Confirmation.model_validate_json(obj)

    async def delete(self, user_id: uuid.UUID) -> None:
        """Удаление подтверждения для пользователя"""
        key = self._key_name(user_id)
        await self.redis.delete(key)

    async def update(self, conf_new_data: ConfUpdate) -> Confirmation:
        """Создание по дефолту перезапишет существующее подтверждение"""
        return await self.create(ConfCreate.model_validate(conf_new_data))

    def _key_name(self, user_id: uuid.UUID) -> str:
        """Ключ кешируемого значения(одно подтверждение на одного пользователя"""
        return f"confirmation_for_{str(user_id)}"
