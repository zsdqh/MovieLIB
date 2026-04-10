import datetime
from datetime import date, timedelta
from typing import Iterable

from sqlalchemy import select

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.users.domain.dtos import ListOfUsersParams
from backend.src.users.domain.entities import (
    BlockingWithUser,
    Comment,
    CreateBlocking,
    Report,
    ShortUser,
    User,
)
from backend.src.users.domain.interfaces.repository.admin_repo import IAdminRepository
from backend.src.users.infrastructure.db.orm import Blocking as BlockingDB
from backend.src.users.infrastructure.db.orm import Comment as CommentDB
from backend.src.users.infrastructure.db.orm import Report as ReportDB
from backend.src.users.infrastructure.db.orm import User as UserDB
from backend.src.users.infrastructure.utils.userdb_to_domain import userdb_to_domain


class PGAdminRepository(PGRepository, IAdminRepository):
    """Postgres реализация репозитория для администраторских действий"""

    async def user_list(self, params: ListOfUsersParams) -> Iterable[User]:
        stmt = select(UserDB)
        if params.created_before:
            stmt = stmt.where(UserDB.created_at <= params.created_before)

        if params.order_by:
            order_fields = []
            for field in params.order_by:
                if field.startswith("-"):
                    col_name = field[1:]
                    direction = "desc"
                else:
                    col_name = field
                    direction = "asc"

                column = getattr(UserDB, col_name, None)

                if column is None:
                    continue

                if direction == "desc":
                    column = column.desc()
                order_fields.append(column)
            if order_fields:
                stmt = stmt.order_by(*order_fields)

        stmt = stmt.offset(params.page * params.size).limit(params.size)
        res = await self.session.scalars(stmt)
        users = [userdb_to_domain(u) for u in res.all()]
        return users

    async def block_user(self, create_data: CreateBlocking) -> BlockingWithUser:
        obj = BlockingDB(**create_data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj, "user")
        return self._blocking_to_domain(obj)

    @staticmethod
    def _blocking_to_domain(obj: BlockingDB) -> BlockingWithUser:
        """Преобразование блокировки в доменную модель"""
        user = ShortUser(**obj.user.__dict__)
        res = BlockingWithUser(**{**obj.__dict__, "user": user})
        return res

    async def unblock_user(self, blocking_id: int) -> None:
        obj = await self.session.get(BlockingDB, blocking_id)
        if not obj:
            return
        today = datetime.date.today()
        obj.ends_at = datetime.datetime(
            year=today.year, month=today.month, day=today.day
        )
        await self.session.flush()

    async def get_reports(self, start_from: date | None) -> list[Report]:
        if not start_from:
            today = datetime.date.today()
            start_from = today - timedelta(days=7)
        stmt = (
            select(ReportDB)
            .where(ReportDB.created_at >= start_from)
            .options(*ReportDB.get_load_options())
        )
        objs = await self.session.execute(stmt)
        return [self._report_to_domain(r) for r in objs.scalars()]

    @staticmethod
    def _report_to_domain(obj: ReportDB) -> Report:
        """Преобразование отчета в доменную модель"""
        created_by = ShortUser(**obj.user.__dict__)
        user = ShortUser(**obj.created_by.__dict__)
        comment = None
        if obj.comment:
            comment = Comment(**{**obj.comment.__dict__})
        return Report(
            **{
                **obj.__dict__,
                "created_by": created_by,
                "user": user,
                "comment": comment,
            }
        )

    async def delete_comment(self, comment_id: int) -> None:
        obj = await self.session.get(CommentDB, comment_id)
        if not obj:
            return
        await self.session.delete(obj)
        await self.session.flush()

    async def change_comment_policy(self, new_text: str) -> None:
        raise NotImplementedError("Да нет пока comment policy")
