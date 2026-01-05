from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
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

related_movies_table = Table(
    "related_movies",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("related_group_id", ForeignKey("related_groups.id"), primary_key=True),
)


class Type(Base):
    """Тип фильма"""

    __tablename__ = "types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    movies: Mapped[list["Movie"]] = relationship(back_populates="type", lazy="selectin")


class Movie(Base):
    """Класс фильма в БД"""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]

    type_id: Mapped[int] = mapped_column(
        ForeignKey("types.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    type: Mapped[Type] = relationship(back_populates="movies", lazy="joined")

    year: Mapped[int]
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None]
    kp_rating: Mapped[float] = mapped_column(Float(2), nullable=False)
    internal_rating: Mapped[float | None] = mapped_column(Float(2), nullable=True)
    poster_url: Mapped[str]
    backdrop_url: Mapped[str | None]
    length: Mapped[int | None]
    age_rating: Mapped[str | None]
    is_series: Mapped[bool]

    related_movies: Mapped[list["Movie"]] = relationship(
        "RelatedGroup",
        secondary=related_movies_table,
        back_populates="movies",
        lazy="selectin",
    )
    countries: Mapped[list["Country"]] = relationship(
        "Country",
        secondary=movie_country_table,
        back_populates="movies",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("year >= 1600", name="check_actual_year_negative"),
        CheckConstraint("length >= 0", name="check_length_non_negative"),
    )


class RelatedGroup(Base):
    """Группа фильмов, содержащая продолжения/предыстории одного фильма"""

    __tablename__ = "related_groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    movies: Mapped[list[Movie]] = relationship(
        "Movie",
        secondary=related_movies_table,
        back_populates="related_movies",
        lazy="selectin",
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
        lazy="selectin",
    )
