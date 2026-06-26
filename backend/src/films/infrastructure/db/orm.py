import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship, selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from backend.src.db.base import Base

movie_country_table = Table(
    "movie_country",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("country_id", ForeignKey("countries.id"), primary_key=True),
)
movie_genre_table = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)


class Type(Base):
    """Тип фильма"""

    __tablename__ = "types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    movies: Mapped[list["Movie"]] = relationship(back_populates="type", lazy="selectin")


class RelatedGroup(Base):
    """Группа фильмов, содержащая продолжения/предыстории одного фильма"""

    __tablename__ = "related_groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        back_populates="related_group", lazy="selectin"
    )


class Movie(Base):
    """Класс фильма в БД"""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    search_vector: Mapped[TSVECTOR] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('russian', coalesce(name, '')), 'A') ||
            setweight(to_tsvector('russian', coalesce(description, '')), 'B')
            """,
            persisted=True,
        ),
    )

    type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[Type] = relationship(back_populates="movies", lazy="joined")

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("related_groups.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    related_group: Mapped[RelatedGroup | None] = relationship(
        back_populates="movies", lazy="joined"
    )

    year: Mapped[int] = mapped_column(Integer, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None]
    kp_rating: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, index=True)
    votes_sum: Mapped[int] = mapped_column(Integer, server_default="0")
    votes_count: Mapped[int] = mapped_column(Integer, server_default="0")
    poster_url: Mapped[str]
    backdrop_url: Mapped[str | None]
    length: Mapped[int | None]
    age_rating: Mapped[int | None]
    is_series: Mapped[bool] = mapped_column(index=True)
    is_partial: Mapped[bool] = mapped_column(nullable=False)

    countries: Mapped[list["Country"]] = relationship(
        "Country",
        secondary=movie_country_table,
        back_populates="movies",
        lazy="selectin",
    )
    genres: Mapped[list["Genre"]] = relationship(
        "Genre", secondary=movie_genre_table, back_populates="movies", lazy="selectin"
    )
    person_movies: Mapped[list["PersonMovie"]] = relationship(
        back_populates="movie", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("year >= 1600", name="check_actual_year_negative"),
        CheckConstraint("length >= 0", name="check_length_non_negative"),
        Index("idx_movies_search", "search_vector", postgresql_using="gin"),
    )

    def get_internal_rating(self) -> float:
        """Расчет внутреннего рейтинга фильма"""
        if self.votes_count == 0:
            return 0
        return round(self.votes_sum / self.votes_count, 2)

    @staticmethod
    def get_load_options() -> list[_AbstractLoad]:
        """Опции загрузки связанных полей при запросе"""
        return [
            selectinload(Movie.genres),
            selectinload(Movie.countries),
            selectinload(Movie.person_movies).joinedload(PersonMovie.person),
            selectinload(Movie.person_movies).joinedload(PersonMovie.profession),
            joinedload(Movie.related_group).selectinload(RelatedGroup.movies),
        ]


class Country(Base):
    """Страны-производители фильмов"""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)

    movies: Mapped[list[Movie]] = relationship(
        "Movie",
        secondary=movie_country_table,
        back_populates="countries",
        lazy="dynamic",
    )


class Genre(Base):
    """Жанры фильмов"""

    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    movies: Mapped[list[Movie]] = relationship(
        "Movie",
        secondary=movie_genre_table,
        back_populates="genres",
        lazy="dynamic",
    )


class Profession(Base):
    """Профессия участника съемочной группы"""

    __tablename__ = "professions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    person_movies: Mapped[list["PersonMovie"]] = relationship(
        back_populates="profession", lazy="dynamic", cascade="all, delete-orphan"
    )


class Person(Base):
    """Участник съемочной группы"""

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str]
    photo_url: Mapped[str | None]
    birthday: Mapped[datetime.date | None]
    is_partial: Mapped[bool] = mapped_column(nullable=False)

    person_movies: Mapped[list["PersonMovie"]] = relationship(
        back_populates="person", lazy="selectin", cascade="all, delete-orphan"
    )

    @staticmethod
    def get_load_options() -> list[_AbstractLoad]:
        """Опции загрузки связанных полей при запросе"""
        return [
            selectinload(Person.person_movies).joinedload(PersonMovie.movie),
            selectinload(Person.person_movies).joinedload(PersonMovie.profession),
        ]


class PersonMovie(Base):
    """
    Участие человека в создании фильма(участник съемочной группы)

    Сложная связь многие-ко-многим с дополнительным полем profession
    """

    __tablename__ = "person_movie"
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    profession_id: Mapped[int] = mapped_column(
        ForeignKey("professions.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    description: Mapped[str | None]

    person: Mapped[Person] = relationship(back_populates="person_movies", lazy="joined")
    movie: Mapped[Movie] = relationship(back_populates="person_movies", lazy="joined")
    profession: Mapped[Profession] = relationship(
        back_populates="person_movies", lazy="joined"
    )
