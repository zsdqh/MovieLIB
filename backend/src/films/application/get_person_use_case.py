from backend.src.films.application.person_use_case import PersonUseCase
from backend.src.films.domain.entities.crud import CreatePerson
from backend.src.films.domain.entities.entities import Person
from backend.src.films.domain.exceptions import PersonNotFoundException


class GetPersonUseCase(PersonUseCase):
    """Получение данных о фильме"""

    async def __call__(self, person_id: int, refresh: bool = False) -> Person:
        """
        Сначала фильм берется из внутреннего хранилища, если не найден,
        то данные берутся из внешнего api и помещаются во внутреннее хранилище
        """
        person = None
        if not refresh:
            async with self.internal_uow as internal:
                person = await internal.persons.get_person_by_id(person_id)
            if person:
                return person

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
                person = await db.films.create_person(create_data, refresh=refresh)
                return person
