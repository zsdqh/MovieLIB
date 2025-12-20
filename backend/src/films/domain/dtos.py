from datetime import datetime

from pydantic import BaseModel, Field


class BasePersonDTO(BaseModel):
    """Общие данные о человеке"""

    id: int
    photo: str
    name: str


class PersonFromFilmDTO(BasePersonDTO):
    """Неполные данные о человеке внутри фильма"""

    en_profession: str = Field(alias="enProfession")


class ShortMovieDTO(BaseModel):
    """Неполные данные о фильме, обычно хранящиеся как дополнительная информация"""

    id: int


class PersonDTO(BasePersonDTO):
    """Полные данные о человеке"""

    birthday: datetime
    movies: list[ShortMovieDTO]


class MovieDTO(BaseModel):
    """Данные о фильме, приходящие извне"""

    id: int
    name: str
    type: str
    year: int
    description: str | None = None
    short_description: str | None = Field(alias="shortDescription")
    slogan: str | None = None
    rating: dict[str, float | None]
    movie_length: int | None = Field(alias="movieLength")
    series_length: int | None = Field(alias="seriesLength")
    age_rating: int | None = Field(alias="ageRating")
    poster: dict[str, str]
    backdrop: dict[str, str | None] | None = None
    genres: list[dict[str, str]]
    countries: list[dict[str, str]]
    persons: list[PersonFromFilmDTO]
    is_series: bool = Field(alias="isSeries")
    sequels_and_prequels: list[ShortMovieDTO] = Field(
        alias="sequelsAndPrequels", default=[]
    )
