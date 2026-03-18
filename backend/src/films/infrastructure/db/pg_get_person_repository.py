from sqlalchemy import select

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.entities import Person
from backend.src.films.domain.interfaces.get_person_repository import (
    IGetPersonRepository,
)
from backend.src.films.infrastructure.db.orm import Person as PersonDB
from backend.src.films.infrastructure.utils.persondb_to_domain import persondb_to_domain


class PGGetPersonRepository(PGRepository, IGetPersonRepository):
    """Реализация репозитория для получения фильмов из БД"""

    async def get_person_by_id(self, person_id: int) -> Person | None:
        stmt = (
            select(PersonDB)
            .where(PersonDB.id == person_id)
            .options(*PersonDB.get_load_options())
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj or obj.is_partial:
            return None
        return persondb_to_domain(obj)

    async def get_persons_by_id(self, person_ids: list[int]) -> list[Person]:
        raise NotImplementedError()
