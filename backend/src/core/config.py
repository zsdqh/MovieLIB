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


class JWTSettings(BaseSettings):
    """Настройки для работы с jwt"""

    access_ttl: int = 60 * 15  # 15 минут
    refresh_ttl: int = 30 * 24 * 60 * 60  # 30 дней
    algorithm: str = "HS256"
    secret_key: str = "a-string-secret-at-least-256-bits-long"


class AWSSettings(BaseSettings):
    """Настройки AWS SES"""

    aws_url: str = "http://localstack:4566"
    aws_access_key_id: str = "aws_key"
    aws_secret_access_key: str = "aws_secret"


class RedisSettings(BaseSettings):
    """Настройки redis"""

    redis_url: str = "redis://redis:6379"
    code_ttl: int = 60 * 5  # 5 минут


class Settings(BaseSettings):
    """Основные настройки проекта"""

    app_name: str = "MovieLIB"
    db: DatabaseSettings = DatabaseSettings()
    auth: JWTSettings = JWTSettings()
    aws: AWSSettings = AWSSettings()
    redis: RedisSettings = RedisSettings()
    email: str = "default@gmail.com"
    tokens: list[str] = []
    base_url: str = "https://api.poiskkino.dev/v1.4"
    test_mode: bool = False
