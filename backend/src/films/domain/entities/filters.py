from enum import StrEnum

from pydantic import BaseModel

from backend.src.films.domain.entities.constants import Genre, MovieType


class Priority(StrEnum):
    """
    Приоритеты жанра, работают в 2 разных режимах:

    - mandatory + exclude
    - optional.

    OPTIONAL: результат будет иметь какой-либо жанр из списка

    MANDATORY: результат будет иметь все жанры из списка

    EXCLUDE: результат точно не будет иметь этот жанр
    """

    OPTIONAL = ""
    MANDATORY = "+"
    EXCLUDE = "!"


class FilterWithPriority(BaseModel):
    """Класс для фильтрации по жанрам(жанр+приоритет фильтрации)"""

    name: Genre | MovieType
    priority: Priority = Priority.OPTIONAL

    def __str__(self) -> str:
        return str(self.priority) + str(
            str(self.name) if isinstance(self.name, Genre) else int(self.name)
        )


class RandomParams(BaseModel):
    """Параметры для случайного поиска фильма"""

    type_number: list[FilterWithPriority] | None = None
    is_series: bool | None = None
    year: str | None = None
    rating: str | None = None
    genres: list[FilterWithPriority] | None = None
    countries: list[str] | None = None


def parse_genre_with_priority(
    value: str,
) -> FilterWithPriority:
    """Парсинг строки в фильтр с параметрами"""
    priority = Priority.OPTIONAL
    name_str = value
    if value.startswith("+"):
        priority = Priority.MANDATORY
        name_str = value[1:]
    elif value.startswith("!"):
        priority = Priority.EXCLUDE
        name_str = value[1:]
    try:
        name = Genre(name_str.strip())
    except ValueError as e:
        raise ValueError(f"Invalid value for Genre: {name_str}") from e
    return FilterWithPriority(name=name, priority=priority)


def parse_movie_type_with_priority(
    value: str,
) -> FilterWithPriority:
    """Парсинг строки в фильтр с параметрами"""
    priority = Priority.OPTIONAL
    name_str = value
    if value.startswith("+"):
        priority = Priority.MANDATORY
        name_str = value[1:]
    elif value.startswith("!"):
        priority = Priority.EXCLUDE
        name_str = value[1:]
    try:
        name = MovieType(int(name_str))
    except ValueError as e:
        raise ValueError(f"Invalid value for MovieType: {name_str}") from e
    return FilterWithPriority(name=name, priority=priority)


class FilmParams(RandomParams):
    """Параметры, которые можно указывать для обычного поиска"""

    person_id: int | None = None
