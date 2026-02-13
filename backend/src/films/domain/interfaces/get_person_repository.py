import abc

from backend.src.films.domain.entities.entities import Person


class IGetPersonRepository(abc.ABC):
    """Интерфейс получения данных о человеке из внешнего источника"""

    @abc.abstractmethod
    async def get_person_by_id(self, person_id: int) -> Person | None:
        """Получение информации о человеке"""

    @abc.abstractmethod
    async def get_persons_by_id(self, person_ids: list[int]) -> list[Person]:
        """Получение информации о списке человек"""
