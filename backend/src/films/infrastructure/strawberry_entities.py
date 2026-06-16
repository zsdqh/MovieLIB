import functools
from typing import Protocol, TypeVar

import strawberry

from backend.src.films.domain.entities.constants import Profession
from backend.src.films.domain.entities.entities import (
    MovieFromPerson as DomainMovieFromPerson,
)
from backend.src.films.domain.entities.entities import Person as DomainPerson
from backend.src.films.domain.entities.entities import Rating as DomainRating

strawberrize = functools.partial(
    strawberry.experimental.pydantic.type, all_fields=True, include_computed=True
)

DomainInstance_contra = TypeVar("DomainInstance_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


class MypyStrawberryStub(Protocol[DomainInstance_contra, T_co]):
    """Стаб для того, чтобы динамический strawberry работал статически"""

    @staticmethod
    def from_pydantic(instance: DomainInstance_contra) -> T_co:
        """Превращение доменной модели в strawberry модель"""


@strawberrize(model=DomainRating)
class Rating:
    """strawberry класс для рейтинга"""


@strawberrize(model=DomainMovieFromPerson)
class MovieFromPerson:
    """strawberry класс для фильма внутри персоны"""

    profession: Profession

    @strawberry.field
    def ru_profession(self) -> str:
        """Русское название профессии"""
        return str(self.profession)


@strawberrize(model=DomainPerson)
class Person(MypyStrawberryStub[DomainPerson, "Person"]):
    """strawberry класс для персоны"""
