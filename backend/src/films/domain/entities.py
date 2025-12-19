from enum import StrEnum

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


class MovieType(StrEnum):
    """Типы фильмов"""

    MOVIE = "фильм"
    TV_SERIES = "телесериал"
    CARTOON = "мультфильм"
    ANIMATED_SERIES = "мультсериал"
    ANIME = "аниме"


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


class RandomParams(BaseModel):
    """Параметры, которые можно указывать для случайного поиска"""

    type: MovieType | None = None
    is_series: bool | None = None
    year: str | None = None
    kp_rating: float | None = None
    age_rating: str | None = None
    genres: list[Genre] | None = None
    countries: list[str] | None = None


class FilmParams(RandomParams):
    """Параметры, которые можно указывать для обычного поиска"""

    person_id: int | None = None
