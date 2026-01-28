from datetime import datetime

from pydantic import BaseModel

from backend.src.films.domain.entities.constants import Genre, MovieType
from backend.src.films.domain.entities.entities import (
    Country,
    ShortMovie,
    ShortPerson,
)


# pylint: disable=R0801
class CreateMovie(BaseModel):
    """Данные для создания нового фильма в бд"""

    id: int
    name: str
    type_number: MovieType
    year: int
    description: str | None = None
    short_description: str | None = None
    votes_sum: int = 0
    votes_count: int = 0
    kp_rating: float = 0
    movie_length: int | None = None
    series_length: int | None = None
    age_rating: int | None = None
    poster: str
    is_partial: bool = False
    backdrop: str | None = None
    genres: list[Genre] = []
    countries: list[Country] = []
    persons: list[ShortPerson] = []
    is_series: bool
    sequels_and_prequels: list[ShortMovie] = []


# pylint: enable=R0801


class CreatePartialMovie(CreateMovie):
    """Данные для создания нового фильма частично"""

    type_number: MovieType = MovieType.MOVIE
    year: int = 2000
    poster: str = ""
    is_partial: bool = True
    is_series: bool = False


class CreatePerson(BaseModel):
    """Данные для создания человека"""

    id: int
    photo: str
    name: str
    birthday: datetime
    movies: list[ShortMovie] = []


class CreatePartialPerson(CreatePerson):
    """Неполные данные о человеке для создания"""

    photo: str = ""
    name: str = ""
    birthday: datetime = datetime(year=2000, month=1, day=1)
