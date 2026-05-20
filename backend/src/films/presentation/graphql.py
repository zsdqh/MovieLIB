import strawberry
from strawberry.fastapi import GraphQLRouter

from backend.src.core.container import Container
from backend.src.films.application.get_person_use_case import GetPersonUseCase
from backend.src.films.infrastructure.strawberry_entities import Person


@strawberry.type
class PersonQuery:
    """Query для запросов по персонам"""

    @strawberry.field
    async def get_person(
        self,
        person_id: int,
    ) -> Person:
        """Получение информации о персоне по id"""
        external_uow = Container.poiskkono_person_uow()
        internal_uow = Container.db_get_person_uow()
        db_uow = Container.db_film_uow()

        person = await GetPersonUseCase(external_uow, internal_uow, db_uow)(person_id)
        res = Person.from_pydantic(person)
        return res


schema = strawberry.Schema(query=PersonQuery)
graph_router = GraphQLRouter(schema)
