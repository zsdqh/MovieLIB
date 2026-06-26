from pydantic import BaseModel


class LoginDTO(BaseModel):
    """Логин и пароль для входа"""

    username: str
    password: str
