import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.auth.users.infrastructure.db.orm import User
from backend.src.db.base import Base


class Confirmation(Base):
    """
    Подтверждение почты аккаунта пользователя

    Неподтвержденный пользователь не может взаимодействовать с системой
    """

    __tablename__ = "confirmations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    user: Mapped[User] = relationship(lazy="joined")
    token: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        """Человекочитаемый вывод подтверждения"""
        return f"Confirmation(id={self.id}, user_id={self.user_id})"
