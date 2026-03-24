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


class OrderableField(StrEnum):
    """Поля, по которым доступна сортировка"""

    RATING = "rating.kp"
    NAME = "name"
    YEAR = "year"
    TYPE = "typeNumber"

    @classmethod
    def ru_fields(cls) -> dict[str, str]:
        """Названия полей на русском с их английским эквивалентом"""
        return {
            "рейтинг KinoPoisk": cls.RATING,
            "название": cls.NAME,
            "год выпуска": cls.YEAR,
            "тип": cls.TYPE,
        }


class MovieType(IntEnum):
    """Типы фильмов"""

    MOVIE = 1
    TV_SERIES = 2
    CARTOON = 3
    ANIME = 4
    ANIMATED_SERIES = 5
    REMAKE = 6

    def __str__(self) -> str:
        """Маппинг типа к русскому названию"""
        translations = {
            MovieType.MOVIE: "Фильм",
            MovieType.TV_SERIES: "Сериал",
            MovieType.CARTOON: "Мультфильм",
            MovieType.ANIME: "Аниме",
            MovieType.ANIMATED_SERIES: "Мультсериал",
            MovieType.REMAKE: "Ремейк",
        }
        return translations[self]

    @classmethod
    def from_api(cls, type_name: str) -> "MovieType":
        """Преобразование английского названия в номер типа"""
        mapping = {
            "movie": 1,
            "tv-series": 2,
            "cartoon": 3,
            "anime": 4,
            "animated-series": 5,
            "remake": 6,
        }
        try:
            return cls(mapping[type_name])
        except KeyError as e:
            raise ValidationError() from e


class Genre(StrEnum):
    """Жанры фильмов с названиями в виде слагов"""

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


# Поля, которые необходимо получить из стороннего api для уменьшения размера ответа
movie_select_fields = [
    "id",
    "name",
    "description",
    "shortDescription",
    "typeNumber",
    "isSeries",
    "year",
    "rating",
    "ageRating",
    "movieLength",
    "seriesLength",
    "genres",
    "countries",
    "poster",
    "backdrop",
    "persons",
    "sequelsAndPrequels",
]

person_select_fields = [
    "id",
    "name",
    "photo",
    "birthday",
    "movies",
]

# Поля, которые не должны быть None при поиске в api
movie_not_null_fields = [
    "id",
    "name",
    "description",
    "typeNumber",
    "year",
    "rating.kp",
    "poster.url",
]
person_not_null_fields = ["id", "photo", "name", "enProfession"]
