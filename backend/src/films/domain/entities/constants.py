from enum import IntEnum, StrEnum

from pydantic import ValidationError


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

    @staticmethod
    def from_api(type_name: str) -> int:
        """Преобразование английского названия в номер типа"""
        mapping = {
            "movie": 1,
            "tv-series": 2,
            "cartoon": 3,
            "anime": 4,
            "animated-series": 5,
        }
        try:
            return mapping[type_name]
        except KeyError as e:
            raise ValidationError() from e


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
