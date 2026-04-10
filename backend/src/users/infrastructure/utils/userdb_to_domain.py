from backend.src.users.domain.entities import User
from backend.src.users.infrastructure.db.orm import User as UserDB
from backend.src.users.infrastructure.utils.listdb_to_domain import listbd_to_domain


def userdb_to_domain(obj: UserDB) -> User:
    """Приведение записи из БД в pydantic модель"""
    lists = [listbd_to_domain(lst) for lst in obj.lists]
    return User(**obj.__dict__, user_lists=lists)
