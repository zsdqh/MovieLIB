from typing import Any

import httpx
from pydantic import ValidationError

from backend.src.films.domain.dtos import PersonDTO
from backend.src.films.domain.entities.constants import (
    person_select_fields,
)
from backend.src.films.domain.entities.entities import Person
from backend.src.films.domain.exceptions import NotEnoughDataException
from backend.src.films.domain.interfaces.get_person_repository import (
    IGetPersonRepository,
)
from backend.src.films.infrastructure.utils.person_to_domain import (
    person_to_domain,
)

AnyDict = dict[str, Any]


class PoiskkinoGetPersonRepository(IGetPersonRepository):
    """Реализация репозитория для взаимодействия со сторонним API"""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Получение клиента для запросов по сети"""
        self.client = client

    async def get_persons_by_name(self, query: str) -> list[Person]:
        resp = await self.client.get(
            "person/search", params={"query": query, "limit": 250}
        )
        data = resp.json().get("docs", [])
        normalized = self._normalize_person_list(data)
        return [person_to_domain(normal) for normal in normalized]

    async def get_person_by_id(self, person_id: int) -> Person | None:
        resp = await self.client.get(f"person/{person_id}")
        normalized = self._normalize_person(dict(resp.json()))
        if not normalized:
            raise NotEnoughDataException("участника съемочной группы")
        return person_to_domain(normalized)

    async def get_persons_by_id(self, person_ids: list[int]) -> list[Person]:
        if not person_ids:
            return []
        resp = await self.client.get(
            "person",
            params={"id": person_ids, "selectFields": person_select_fields},
        )
        data = resp.json().get("docs", [])
        normalized = self._normalize_person_list(data)
        return [person_to_domain(normal) for normal in normalized]

    def _normalize_person_list(self, person_list: list[AnyDict]) -> list[PersonDTO]:
        """Нормализация списка людей"""
        res = []
        for person in person_list:
            normal = self._normalize_person(person)
            if not normal:
                continue
            res.append(normal)
        return res

    def _normalize_person(self, person_data: AnyDict) -> PersonDTO | None:
        """Нормализация приходящих данных о людях"""
        try:
            movies = list(
                filter(
                    lambda f: f.get("name") and f.get("enProfession"),
                    person_data.get("movies", []),
                )
            )
            person_data["movies"] = movies
            return PersonDTO.model_validate(person_data)
        except ValidationError:
            # for error in e.errors():
            #     if error.get("input") is None:
            #         if error.get("loc")[0] not in person_not_null_fields:
            #             raise
            #     else:
            #         raise
            return None
