from enum import StrEnum

from pydantic import BaseModel

from backend.src.films.domain.entities import Genre, MovieType


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
        return str(self.priority) + str(self.name)


class RandomParams(BaseModel):
    """Параметры, которые можно указывать для случайного поиска"""

    type_number: list[FilterWithPriority] | None = None
    is_series: bool | None = None
    year: str | None = None
    rating: str | None = None
    genres: list[FilterWithPriority] | None = None
    countries: list[str] | None = None


class FilmParams(RandomParams):
    """Параметры, которые можно указывать для обычного поиска"""

    person_id: int | None = None
