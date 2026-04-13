import uuid

from sqlalchemy import Executable, select
from sqlalchemy.exc import IntegrityError

from backend.src.core.domain.exceptions import AlreadyExistsException, NotFoundException
from backend.src.db.infrastructure.pg_repository import (
    PGRepository,
)
from backend.src.users.domain.entities import (
    Comment,
    CreateReport,
    Report,
    ShortUser,
    User,
    UserRegister,
    UserUpdate,
)
from backend.src.users.domain.interfaces.repository.user_repo import IUserRepository
from backend.src.users.infrastructure.db.orm import Report as ReportDB
from backend.src.users.infrastructure.db.orm import User as UserDB
from backend.src.users.infrastructure.utils.userdb_to_domain import userdb_to_domain


class PGUserRepository(PGRepository, IUserRepository):
    """Postgres реализация репозитория для работы с таблицей User"""

    async def add(self, user: UserRegister) -> User:
        """
        Создание нового пользователя в базе

        :param user: схема с данными о регистрируемом пользователе
        :return: созданный пользователь
        :raises UserAlreadyExistsException: если данные пользователя неуникальны
        """
        obj = UserDB(**user.model_dump(mode="json"))
        self.session.add(obj)
        obj.lists = []
        obj.blockings = []

        await self._flush_or_exception()

        return userdb_to_domain(obj)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        """
        Получение пользователя по его id

        :raises UserNotFoundException: если пользователя с заданным id нет в базе
        """
        obj: UserDB = await self._get_or_exception(
            select(UserDB).where(UserDB.id == user_id),
            f"Пользователь с id {user_id} не найден",
        )

        return userdb_to_domain(obj)

    async def get_by_username(self, username: str) -> User:
        """
        Получение пользователя по его имени

        :raises UserNotFoundException: если пользователя с заданной почтой нет в базе
        """
        stmt = select(UserDB).where(UserDB.username == username)
        result = await self._get_or_exception(
            stmt, f"Пользователь с именем {username} не найден"
        )
        return userdb_to_domain(result)

    async def delete(self, user_id: uuid.UUID) -> None:
        """
        Удаление пользователя из базы

        :raises UserNotFoundException: если пользователя с заданным id нет в базе
        """
        obj = await self._get_or_exception(
            select(UserDB).where(UserDB.id == user_id),
            f"Пользователь с id {user_id} не найден",
        )

        await self.session.delete(obj)
        await self.session.flush()

    async def update(self, update_data: UserUpdate) -> User:
        """Изменение полей пользователя"""
        stmt = select(UserDB).where(UserDB.id == update_data.id)
        obj = await self._get_or_exception(
            stmt, f"Пользователь с id {update_data.id} не найден"
        )
        for name, value in update_data.model_dump(exclude={"id"}).items():
            if value:
                setattr(obj, name, value)

        await self._flush_or_exception()
        await self.session.refresh(obj)
        return userdb_to_domain(obj)

    async def remove_avatar(self, user_id: uuid.UUID) -> str | None:
        stmt = select(UserDB).where(UserDB.id == user_id)
        obj = await self._get_or_exception(
            stmt, f"Пользователь с id {user_id} не найден"
        )
        avatar = obj.avatar_url
        obj.avatar_url = None
        await self._flush_or_exception()
        await self.session.refresh(obj)
        return avatar

    async def report_user(self, report_data: CreateReport) -> Report:
        """Создание жалобы на пользователя"""
        obj = ReportDB(**report_data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return self._report_to_domain(obj)

    @staticmethod
    def _report_to_domain(report: ReportDB) -> Report:
        """Преобразование жалобы в domain объект"""
        user = ShortUser(**report.user.__dict__)
        created_by = ShortUser(**report.created_by.__dict__)
        comment = (
            Comment(**{**report.comment.__dict__, "answers": [], "user": user})
            if report.comment
            else None
        )
        return Report(
            **{
                **report.__dict__,
                "user": user,
                "created_by": created_by,
                "comment": comment,
            }
        )

    async def _get_or_exception(self, statement: Executable, message: str) -> UserDB:
        """Получение объекта из БД или выброс 404 кода"""
        result = await self.session.execute(statement)
        obj: UserDB | None = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException(detail=message)
        return obj

    async def _flush_or_exception(self) -> None:
        """Попытка внесения изменений с выбросом ошибки при неудаче"""
        try:
            await self.session.flush()
        except IntegrityError as e:
            e_text = str(e.orig)
            if "email" in e_text:
                resp_text = "Почта уже используется"
            elif "username" in e_text:
                resp_text = "Имя пользователя уже используется"
            else:
                resp_text = "Неожиданная ошибка при регистрации"
            raise AlreadyExistsException(detail=resp_text) from e
