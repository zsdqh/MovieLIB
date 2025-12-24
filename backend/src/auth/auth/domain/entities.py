import uuid
from typing import Any

from pydantic import BaseModel, EmailStr, model_validator


class TokenUser(BaseModel):
    """Данные о пользователе"""

    valid_refresh_id: int
    username: str
    sub: uuid.UUID
    is_admin: bool
    is_activated: bool
    is_blocked: bool
    email: EmailStr
    avatar_url: str = ""

    @model_validator(mode="before")
    def alias_sub_avatar(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Подстановка id, если не передан sub"""
        if "id" in values and "sub" not in values:
            values["sub"] = values["id"]
        if "avatar_url" in values and values["avatar_url"] is None:
            values["avatar_url"] = ""
        return values
