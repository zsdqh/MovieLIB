from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Настройки БД"""

    model_config = SettingsConfigDict(env_prefix="database_")
    username: str = "postgres"
    password: str = "postgres"
    port: int = 5432
    name: str = "postgres"

    @property
    def url(self) -> str:
        """Формирование полного URL для подключения к БД"""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.username,
                password=self.password,
                host="postgres",
                port=self.port,
                path=self.name,
            )
        )


class Settings(BaseSettings):
    """Основные настройки проекта"""

    app_name: str = "MovieLIB"
    email: str = "default@gmail.com"
    db: DatabaseSettings = DatabaseSettings()
