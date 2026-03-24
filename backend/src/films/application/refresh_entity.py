"""Принудительное обновление сущностей из внешнего API и запись в БД."""

from backend.src.films.application.person_use_case import PersonUseCase
from backend.src.films.domain.entities.crud import CreatePerson
from backend.src.films.domain.entities.entities import Person
from backend.src.films.domain.exceptions import (
    PersonNotFoundException,
)


class RefreshPersonFromExternalUseCase(PersonUseCase):
    """Перезагрузка персоны из внешнего API и upsert в локальной БД."""

    async def __call__(self, person_id: int) -> Person:
        async with self.external_uow as external:
            person = await external.persons.get_person_by_id(person_id)
            if not person:
                raise PersonNotFoundException(person_id)
        async with self.db_uow as db:
            movies = [
                {
                    **movie.model_dump(),
                    "kp_rating": (
                        movie.rating.kp_rating if movie.rating.kp_rating else 0
                    ),
                    "description": movie.description if movie.description else "",
                }
                for movie in person.movies
            ]
            create_data = CreatePerson.model_validate(
                {**person.model_dump(), "movies": movies}
            )
            return await db.films.create_person(create_data, refresh=True)
