from datetime import datetime, timezone

from backend.src.users.domain.entities import Blocking, User
from backend.src.users.infrastructure.db.orm import User as UserDB
from backend.src.users.infrastructure.utils.listdb_to_domain import listbd_to_domain


def userdb_to_domain(obj: UserDB) -> User:
    """Приведение записи из БД в pydantic модель"""
    lists = [listbd_to_domain(lst) for lst in obj.lists]
    now = datetime.now(timezone.utc)
    active_blockings = []
    for blocking in obj.blockings:
        ends_at = blocking.ends_at
        if ends_at is not None:
            if ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)
            if ends_at <= now:
                continue
        active_blockings.append(Blocking(**blocking.__dict__))

    return User(
        **obj.__dict__,
        user_lists=lists,
        active_blockings=active_blockings,
    )
