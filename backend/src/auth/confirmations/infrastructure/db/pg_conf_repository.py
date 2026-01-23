import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.src.auth.confirmations.domain.entities import (
    ConfCreate,
    Confirmation,
    ConfUpdate,
)
from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.auth.confirmations.infrastructure.db.orm import (
    Confirmation as ConfirmationDB,
)
from backend.src.core.domain.exceptions import AlreadyExistsException, NotFoundException
from backend.src.users.infrastructure.db.repositories.pg_repository import (
    PGRepository,
)


class PGConfRepository(PGRepository, IConfRepository):
    """Реализация репозитория для работы с подтверждениями в БД"""

    async def create(self, conf_data: ConfCreate) -> Confirmation:
        """Создание подтверждения"""
        obj = ConfirmationDB(token=conf_data.token, user_id=conf_data.user_id)
        self.session.add(obj)
        try:
            await self.session.flush()
            return self._to_domain(obj)
        except IntegrityError as e:
            raise AlreadyExistsException(
                "Confirmation for this user already exists"
            ) from e

    async def get_by_user_id(self, user_id: uuid.UUID) -> Confirmation:
        obj = await self._get_confirmation_by_uuid(user_id)
        return self._to_domain(obj)

    async def delete(self, user_id: uuid.UUID) -> None:
        obj = await self._get_confirmation_by_uuid(user_id)
        await self.session.delete(obj)

    async def update(self, conf_new_data: ConfUpdate) -> Confirmation:
        obj = await self._get_confirmation_by_uuid(conf_new_data.user_id)
        for attr, value in conf_new_data.model_dump(exclude={"id", "user_id"}).items():
            setattr(obj, attr, value)
        await self.session.flush()
        return self._to_domain(obj)

    def _to_domain(self, obj: ConfirmationDB) -> Confirmation:
        """Преобразование объекта БД в pydantic модель"""
        return Confirmation(id=obj.id, user_id=obj.user_id, token=obj.token)

    async def _get_confirmation_by_uuid(self, user_id: uuid.UUID) -> ConfirmationDB:
        """
        Получение подтверждения по id пользователя
        с выбрасыванием ошибки при отсутствии
        """
        statement = select(ConfirmationDB).where(ConfirmationDB.user_id == user_id)
        res = await self.session.execute(statement)
        obj = res.scalar_one_or_none()
        if not obj:
            raise NotFoundException(f"Confirmation for {user_id} not found")
        return obj
