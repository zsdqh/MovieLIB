from datetime import datetime

from pydantic import BaseModel, Field

from backend.src.films.domain.entities.constants import Genre, MovieType, Profession
from backend.src.films.domain.entities.entities import (
    Country,
)


# pylint: disable=R0801
class CreateMovie(BaseModel):
    """Данные для создания нового фильма в бд"""

    id: int
    name: str
    type_number: MovieType = Field(alias="type")
    year: int
    description: str | None = None
    short_description: str | None = None
    votes_sum: int = 0
    votes_count: int = 0
    kp_rating: float = 0
    length: int
    age_rating: int | None = None
    poster: str
    is_partial: bool = False
    backdrop: str | None = None
    is_series: bool
    genres: list[Genre] = []
    countries: list[Country] = []
    persons: list["CreatePartialPerson"] = []
    sequels_and_prequels: list["CreatePartialMovie"] = []

    @staticmethod
    def get_excluded_fields() -> set[str]:
        """Исключаемые поля при создании экземпляра в БД"""
        return {
            "type_number",
            "poster",
            "backdrop",
            "countries",
            "genres",
            "persons",
            "sequels_and_prequels",
        }


# pylint: enable=R0801


class CreatePartialMovie(CreateMovie):
    """Данные для создания нового фильма частично"""

    type_number: MovieType = MovieType.MOVIE
    description: str = ""
    year: int = 2000
    poster: str = ""
    is_partial: bool = True
    is_series: bool = False
    length: int = 0


class CreatePerson(BaseModel):
    """Данные для создания человека"""

    id: int
    photo: str
    name: str
    birthday: datetime
    is_partial: bool = False
    profession: Profession | None = None
    movies: list[CreatePartialMovie] = []

    @staticmethod
    def get_excluded_fields() -> set[str]:
        """Исключаемые поля при создании экземпляра в БД"""
        return {"photo", "name", "profession", "movies"}


class CreatePartialPerson(CreatePerson):
    """Неполные данные о человеке для создания"""

    photo: str = ""
    name: str = ""
    is_partial: bool = True
    birthday: datetime = datetime(year=2000, month=1, day=1)
