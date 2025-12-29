import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


class Templates(StrEnum):
    """Названия шаблонов сообщений"""

    EMAIL_CONFIRMATION = "EmailConfirmation"
    PASSWORD_CONFIRMATION = "PasswordResetConfirmation"


class ConfBase(BaseModel):
    """Стандартные данные подтверждений"""

    user_id: uuid.UUID
    token: str


class ConfCreate(ConfBase):
    """Данные для создания подтверждения"""


class ConfUpdate(ConfBase):
    """Данные для обновления подтверждения"""


class Confirmation(ConfBase):
    """Данные для внутренней передачи подтверждения"""

    id: int | str


class ConfPublic(BaseModel):
    """Публично видимые данные подтверждения"""

    id: int | str
    user_id: uuid.UUID


class TemplateData(BaseModel):
    """Данные, передаваемые в шаблон сообщения"""

    token: str
    username: str


class EmailData(BaseModel):
    """Данные для отправки сообщений"""

    destination: list[str]
    template_name: Templates
    template_data: TemplateData


class NewPassword(BaseModel):
    """Новый пароль с проверкой длинны"""

    password: str = Field(min_length=8, max_length=100)
