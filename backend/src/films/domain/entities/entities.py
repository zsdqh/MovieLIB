from datetime import datetime

from pydantic import BaseModel

from backend.src.films.domain.dtos import BasePersonDTO
from backend.src.films.domain.entities.constants import Genre, MovieType, Profession


class ShortMovie(BaseModel):
    """Неполные данные о фильме, обычно хранящиеся как дополнительная информация"""

    id: int
    name: str
    poster: str
    type: MovieType


class Person(BasePersonDTO):
    """Полные данные о человеке"""

    birthday: datetime
    movies: list[ShortMovie]


class ShortPerson(BasePersonDTO):
    """Данные о человеке из съемочной группы"""

    profession: Profession


class Rating(BaseModel):
    """Информация о рейтинге фильма(внутреннем и по данным KinoPoisk)"""

    kp_rating: float | None = None
    internal_rating: float | None = None


class Country(BaseModel):
    """Данные о стране"""

    id: int
    name: str


class Movie(BaseModel):
    """Данные о фильме, приходящие извне"""

    id: int
    name: str
    type_number: MovieType
    year: int
    description: str | None = None
    short_description: str | None = None
    rating: Rating
    movie_length: int | None = None
    series_length: int | None = None
    age_rating: int | None = None
    poster: str
    backdrop: str | None = None
    is_series: bool
    genres: list[Genre] = []
    countries: list[Country] = []
    persons: list[ShortPerson] = []
    sequels_and_prequels: list[ShortMovie] = []
