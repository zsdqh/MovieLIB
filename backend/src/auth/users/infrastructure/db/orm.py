"""Основные ORM модели для работы с пользователями"""

import uuid
from datetime import datetime

from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.db.base import Base


class User(Base):
    """
    Класс пользователя в системе

    Заблокированный/неактивированный аккаунт не может взаимодействовать с системой
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_activated: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    valid_refresh_id: Mapped[int] = mapped_column(nullable=False, server_default="0")

    def __repr__(self) -> str:
        """Человекочитаемый минимальный вывод пользователя"""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
