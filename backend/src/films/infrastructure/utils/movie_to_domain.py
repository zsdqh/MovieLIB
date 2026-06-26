from typing import Any

from backend.src.films.domain.dtos import MovieDTO, PersonFromFilmDTO, ShortMovieDTO
from backend.src.films.domain.entities.constants import Genre, MovieType, Profession
from backend.src.films.domain.entities.entities import (
    Country,
    Movie,
    Rating,
    ShortMovie,
    ShortPerson,
)


def parse_atomic_fields(movie_dto: MovieDTO, to_fill: dict[str, Any]) -> None:
    """Получение атомарных значений из dto"""
    to_fill["type"] = MovieType(movie_dto.type_number)
    to_fill["rating"] = Rating(kp_rating=movie_dto.rating.get("kp"))

    to_fill["length"] = movie_dto.movie_length
    if not to_fill["length"]:
        to_fill["length"] = movie_dto.series_length

    to_fill["poster"] = movie_dto.poster.get("url")
    if not to_fill["poster"]:
        to_fill["poster"] = movie_dto.poster.get("previewUrl")

    if movie_dto.backdrop:
        to_fill["backdrop"] = movie_dto.backdrop.get("url")
        if not to_fill["backdrop"]:
            to_fill["backdrop"] = movie_dto.backdrop.get("previewUrl")


def parse_genres(genres: list[dict[str, str]]) -> list[Genre]:
    """Жанры из dto в domain"""
    res = []
    for genre in genres:
        name = genre.get("name")
        if name:
            try:
                res.append(Genre(name))
            except ValueError:
                pass
    return res


def parse_countries(countries: list[dict[str, str | int]]) -> list[Country]:
    """Страны из dto в domain"""
    res = []
    for country in countries:
        country_name = country.get("name")
        if country_name:
            try:
                res.append(Country(name=country_name))
            except ValueError:
                pass
    return res


def parse_persons(persons: list[PersonFromFilmDTO]) -> list[ShortPerson]:
    """Люди из dto в domain"""
    res = []
    for person in persons:
        profession = Profession.from_api(person.en_profession)
        validated = ShortPerson.model_validate(
            {**dict(person), "profession": profession}
        )
        res.append(validated)
    return res


def parse_sequels_and_prequels(
    sequels_and_prequels: list[ShortMovieDTO],
) -> list[ShortMovie]:
    """Продолжения и предыстории из dto в domain"""
    res = []
    for short in sequels_and_prequels:
        short_type = MovieType.from_api(short.type)
        short_poster = short.poster.get("url")
        if not short_poster:
            short_poster = short.poster.get("previewUrl")

        res.append(
            ShortMovie.model_validate(
                {**dict(short), "type": short_type, "poster": short_poster}
            )
        )
    return res


def movie_to_domain(movie_dto: MovieDTO) -> Movie:
    """
    Нормализация и маппинг данных о фильме из dto в domain объект
    """
    re_made: dict[str, Any] = {}
    parse_atomic_fields(movie_dto, re_made)

    re_made["genres"] = parse_genres(movie_dto.genres)
    re_made["countries"] = parse_countries(movie_dto.countries)
    re_made["persons"] = parse_persons(movie_dto.persons)
    re_made["sequels_and_prequels"] = parse_sequels_and_prequels(
        movie_dto.sequels_and_prequels
    )

    return Movie.model_validate({**dict(movie_dto), **re_made})
