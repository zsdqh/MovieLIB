from datetime import date

from pydantic import BaseModel

from backend.src.films.domain.dtos import BasePersonDTO
from backend.src.films.domain.entities.constants import Genre, MovieType, Profession


class ShortMovie(BaseModel):
    """Неполные данные о фильме, обычно хранящиеся как дополнительная информация"""

    id: int
    name: str
    poster: str
    type: MovieType


class Rating(BaseModel):
    """Информация о рейтинге фильма(внутреннем и по данным KinoPoisk)"""

    kp_rating: float | None = None
    internal_rating: float | None = None


class MovieFromPerson(BaseModel):
    """Неполные данные о фильме, вместе с информацией об участии человека в нем"""

    id: int
    name: str
    rating: Rating
    description: str | None  # описание РОЛИ человека в фильме
    profession: Profession


class Person(BasePersonDTO):
    """Полные данные о человеке"""

    birthday: date | None = None
    movies: list[MovieFromPerson]


class ShortPerson(BasePersonDTO):
    """Данные о человеке из съемочной группы"""

    profession: Profession


class Country(BaseModel):
    """Данные о стране"""

    name: str


class Movie(BaseModel):
    """Данные о фильме, приходящие извне"""

    id: int
    name: str
    type: MovieType
    year: int
    description: str
    short_description: str | None = None
    rating: Rating
    length: int | None = None
    age_rating: int | None = None
    poster: str
    backdrop: str | None = None
    is_series: bool
    genres: list[Genre] = []
    countries: list[Country] = []
    persons: list[ShortPerson] = []
    sequels_and_prequels: list[ShortMovie] = []
    similar_movies: list[int] = []


class ExternalExceptionData(BaseModel):
    """Данные об ошибках от внешнего сервиса"""

    message: list[str]
    error: str
    statusCode: int
