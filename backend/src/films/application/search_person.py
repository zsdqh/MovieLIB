from backend.src.films.application.person_use_case import PersonUseCase
from backend.src.films.domain.entities.entities import Person


class GetPersonsByNameUseCase(PersonUseCase):
    """Вариант использования для получения персон по имени"""

    async def __call__(self, query: str) -> list[Person]:
        async with self.external_uow:
            return await self.external_uow.persons.get_persons_by_name(query)
