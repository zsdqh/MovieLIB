from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Основные настройки проекта"""

    app_name: str = "MovieLIB"
    email: str = "default@gmail.com"
