from enum import IntEnum, StrEnum

from pydantic import BaseModel


class Profession(StrEnum):
    """Профессии людей в фильмах"""

    ACTOR = "актер"
    VOICE_ACTOR = "актер дубляжа"
    OPERATOR = "оператор"
    EDITOR = "монтажер"
    COMPOSER = "композитор"
    DESIGNER = "художник"
    DIRECTOR = "режиссер"
    WRITER = "сценарист"
    PRODUCER = "продюсер"

    @classmethod
    def from_api(cls, api_value: str) -> str:
        """Маппинг английского названия профессии к русскому"""
        return str(cls[api_value.upper()].value)


class MovieType(IntEnum):
    """Типы фильмов"""

    MOVIE = 1
    TV_SERIES = 2
    CARTOON = 3
    ANIME = 4
    ANIMATED_SERIES = 5

    def __str__(self) -> str:
        """Маппинг типа к русскому названию"""
        translations = {
            MovieType.MOVIE: "Фильм",
            MovieType.TV_SERIES: "Сериал",
            MovieType.CARTOON: "Мультфильм",
            MovieType.ANIME: "Аниме",
            MovieType.ANIMATED_SERIES: "Мультсериал",
        }
        return translations[self]


class Genre(StrEnum):
    """Жанры фильмов"""

    ANIME = "аниме"
    BIOGRAFIYA = "биография"
    BOEVIK = "боевик"
    VESTERN = "вестерн"
    VOENNYY = "военный"
    DETEKTIV = "детектив"
    DETSKIY = "детский"
    DLYA_VZROSLYH = "для взрослых"
    DOKUMENTALNYY = "документальный"
    DRAMA = "драма"
    IGRA = "игра"
    ISTORIYA = "история"
    KOMEDIYA = "комедия"
    KONCERT = "концерт"
    KOROTKOMETRAZHKA = "короткометражка"
    KRIMINAL = "криминал"
    MELODRAMA = "мелодрама"
    MUZYKA = "музыка"
    MULTFILM = "мультфильм"
    MYUZIKL = "мюзикл"
    NOVOSTI = "новости"
    PRIKLYUCHENIYA = "приключения"
    REALNOE_TV = "реальное ТВ"
    SEMEYNYY = "семейный"
    SPORT = "спорт"
    TOK_SHOU = "ток-шоу"
    TRILLER = "триллер"
    UZHASY = "ужасы"
    FANTASTIKA = "фантастика"
    FILM_NUAR = "фильм-нуар"
    FENTEZI = "фэнтези"
    CEREMONIYA = "церемония"


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
