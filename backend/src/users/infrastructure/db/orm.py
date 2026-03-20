"""Основные ORM модели для работы с пользователями"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship, selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from backend.src.db.base import Base
from backend.src.films.infrastructure.db.orm import Movie


class User(Base):
    """
    Класс пользователя в системе

    Заблокированный/неактивированный аккаунт не может взаимодействовать с системой
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(30), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    is_activated: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )

    valid_refresh_id: Mapped[int] = mapped_column(nullable=False, server_default="0")
    blockings: Mapped[list["Blocking"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    lists: Mapped[list["List"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        """Человекочитаемый минимальный вывод пользователя"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"


class Blocking(Base):
    """Блокировка пользователя с датой окончания и причиной блокировки"""

    __tablename__ = "blockings"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship(back_populates="blockings", lazy="joined")

    reason: Mapped[str | None] = mapped_column(nullable=True)
    ends_at: Mapped[datetime] = mapped_column(nullable=True)

    __table_args__ = (Index("idx_blockings_user_ends_at", "user_id", "ends_at"),)


class List(Base):
    """Списки фильмов пользователя"""

    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    is_public: Mapped[bool] = mapped_column(index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped[User] = relationship(back_populates="lists", lazy="joined")

    list_movies: Mapped[list["ListMovie"]] = relationship(
        back_populates="list", lazy="selectin"
    )

    @staticmethod
    def get_load_options() -> list[_AbstractLoad]:
        """Опции загрузки связанных полей при запросе"""
        return [selectinload(List.list_movies).joinedload(ListMovie.movie)]


class ListMovie(Base):
    """Связующая таблица многие-ко-многим для фильмов и пользовательских списков"""

    __tablename__ = "list_movie"

    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    list: Mapped[List] = relationship(back_populates="list_movies", lazy="joined")

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    movie: Mapped[Movie] = relationship("Movie", lazy="joined")

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"), nullable=False
    )
    __mapper_args__ = {"eager_defaults": True}


class Comment(Base):
    """Комментарий пользователя к фильму"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    answer_to: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    answers: Mapped[list["Comment"]] = relationship(
        backref=backref("parent", remote_side=[id]), lazy="dynamic"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"), nullable=False
    )
    rating: Mapped[int] = mapped_column(server_default=text("0"))
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (
        Index("idx_comments_created_at", "created_at"),
        Index("idx_comments_thread", "answer_to", "created_at"),
    )


class CommentReaction(Base):
    """Реакция пользователя на комментарий(положительная или отрицательная)"""

    __tablename__ = "comment_reactions"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    rating: Mapped[bool] = mapped_column(nullable=False, default=True)


class UserRating(Base):
    """Оценка фильма от пользователя от 1 до 10"""

    __tablename__ = "user_ratings"
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    movie: Mapped[Movie] = relationship("Movie", lazy="joined")

    rating: Mapped[int] = mapped_column(index=True)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 10", name="check_rating_correct"),
    )
