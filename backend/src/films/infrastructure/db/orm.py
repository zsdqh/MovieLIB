import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    name: Mapped[str] = mapped_column(nullable=True)

    movies: Mapped[list["Movie"]] = relationship(
        back_populates="related_group", lazy="selectin"
    )


class Movie(Base):
    """Класс фильма в БД"""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    type: Mapped[Type] = relationship(back_populates="movies", lazy="joined")

    group_id: Mapped[int] = mapped_column(
        ForeignKey("related_groups.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    related_group: Mapped[RelatedGroup] = relationship(
        back_populates="movies", lazy="joined"
    )

    year: Mapped[int]
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None]
    kp_rating: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    votes_sum: Mapped[int] = mapped_column(Integer, server_default="0")
    votes_count: Mapped[int] = mapped_column(Integer, server_default="0")
    poster_url: Mapped[str]
    backdrop_url: Mapped[str | None]
    length: Mapped[int | None]
    age_rating: Mapped[str | None]
    is_series: Mapped[bool]

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
        back_populates="movie", lazy="dynamic", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("year >= 1600", name="check_actual_year_negative"),
        CheckConstraint("length >= 0", name="check_length_non_negative"),
    )


class Country(Base):
    """Страны-производители фильмов"""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

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
    birthday: Mapped[datetime.date]

    person_movies: Mapped[list["PersonMovie"]] = relationship(
        back_populates="person", lazy="dynamic", cascade="all, delete-orphan"
    )


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

    person: Mapped[Person] = relationship(back_populates="person_movies", lazy="joined")
    movie: Mapped[Movie] = relationship(back_populates="person_movies", lazy="joined")
    profession: Mapped[Profession] = relationship(
        back_populates="person_movies", lazy="joined"
    )
