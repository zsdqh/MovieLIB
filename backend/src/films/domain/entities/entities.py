from datetime import datetime

from pydantic import BaseModel

from backend.src.films.domain.dtos import BasePersonDTO, PersonFromFilmDTO
from backend.src.films.domain.entities.constants import Genre, MovieType


class ShortMovie(BaseModel):
    """Неполные данные о фильме, обычно хранящиеся как дополнительная информация"""

    id: int


class Person(BasePersonDTO):
    """Полные данные о человеке"""

    birthday: datetime
    movies: list[ShortMovie]


class Rating(BaseModel):
    """Информация о рейтинге фильма(внутреннем и по данным KinoPoisk)"""

    kp_rating: float | None = None
    internal_rating: float | None = None


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
    backdrop: str
    genres: list[Genre] = []
    countries: list[str] = []
    persons: list[PersonFromFilmDTO] = []
    is_series: bool
    sequels_and_prequels: list[ShortMovie] = []
