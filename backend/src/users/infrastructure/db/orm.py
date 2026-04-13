"""Основные ORM модели для работы с пользователями"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy import text as sql_text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    backref,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
)
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
        nullable=False, server_default=sql_text("now()")
    )

    valid_refresh_id: Mapped[int] = mapped_column(nullable=False, server_default="0")
    blockings: Mapped[list["Blocking"]] = relationship(
        back_populates="user",
        lazy="selectin",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
    lists: Mapped[list["List"]] = relationship(
        back_populates="user",
        lazy="selectin",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Человекочитаемый минимальный вывод пользователя"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"

    @staticmethod
    def get_load_options() -> list[_AbstractLoad]:
        """Опции для загрузки связанных данных"""
        return [
            selectinload(User.lists)
            .joinedload(List.list_movies)
            .joinedload(ListMovie.movie),
            selectinload(User.blockings),
        ]


class Blocking(Base):
    """Блокировка пользователя с датой окончания и причиной блокировки"""

    __tablename__ = "blockings"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship(back_populates="blockings", lazy="joined")

    reason: Mapped[str | None] = mapped_column(nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (Index("idx_blockings_user_ends_at", "user_id", "ends_at"),)


class Comment(Base):
    """Комментарий пользователя к фильму"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]

    answer_to: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    answers: Mapped[list["Comment"]] = relationship(
        backref=backref("parent", remote_side=[id]),
        lazy="selectin",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped[User] = relationship(
        "User",
        lazy="joined",
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=sql_text("now()"), nullable=False
    )
    rating: Mapped[int] = mapped_column(server_default=sql_text("0"))
    movie_id: Mapped[int | None] = mapped_column(
        ForeignKey("movies.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True
    )
    __table_args__ = (
        Index("idx_comments_created_at", "created_at"),
        Index("idx_comments_thread", "answer_to", "created_at"),
        CheckConstraint(
            "NOT (movie_id IS NULL AND answer_to IS NULL)", name="check_comment_target"
        ),
    )


class Report(Base):
    """Жалоба на пользователя о нарушении правил"""

    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=sql_text("now()"), nullable=False
    )
    solved: Mapped[bool]
    reason: Mapped[str | None] = mapped_column(nullable=True)
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    comment: Mapped[Comment] = relationship(
        "Comment",
        lazy="joined",
        passive_deletes=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship("User", lazy="joined", foreign_keys=[user_id])

    created_by_id = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[User] = relationship(
        "User", lazy="joined", foreign_keys=[created_by_id]
    )

    @staticmethod
    def get_load_options() -> list[_AbstractLoad]:
        """Опции для загрузки связанных данных"""
        return [
            joinedload(Report.user),
            joinedload(Report.comment).joinedload(Comment.user),
        ]


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
    user: Mapped[User] = relationship(
        back_populates="lists", lazy="joined", passive_deletes=True
    )

    list_movies: Mapped[list["ListMovie"]] = relationship(
        back_populates="list",
        lazy="selectin",
        passive_deletes=True,
        cascade="all, delete-orphan",
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
    list: Mapped[List] = relationship(
        back_populates="list_movies",
        lazy="joined",
        passive_deletes=True,
    )

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    movie: Mapped[Movie] = relationship(
        "Movie",
        lazy="joined",
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=sql_text("now()"), nullable=False
    )
    __mapper_args__ = {"eager_defaults": True}


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
    reaction: Mapped[bool] = mapped_column(nullable=False, default=True)


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
