import asyncio
from typing import Any, Generator
from unittest.mock import AsyncMock

import redis
from alembic import command
from alembic.config import Config
from redis import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from backend.src.core.config import DatabaseSettings, Settings
from backend.src.core.container import Container
from backend.src.main import create_app
import pytest

from .common import faker, user_data, clean_tokens


def do_run_migrations(db_url: str) -> None:
    """Применение alembic миграций к тестовой базе"""
    alembic_cfg = Config("backend/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


async def create_test_db() -> None:
    """Удаление старой и создание новой тестовой базы для каждой тестовой сессии"""
    engine = Container.engine()
    async with engine.connect() as conn:
        conn = await conn.execution_options()
        try:
            await conn.execute(text("ROLLBACK"))
            await conn.execute(text("DROP DATABASE test"))
        except SQLAlchemyError:
            await conn.execute(text("ROLLBACK"))
        await conn.execute(text("CREATE DATABASE test"))


@pytest.fixture(scope="session")
def container() -> Container:
    """Контейнер с url тестовой базы"""
    asyncio.run(create_test_db())
    container = Container(
        settings=Settings(db=DatabaseSettings(name="test"), test_mode=True),
        email_sender=AsyncMock(),
    )
    do_run_migrations(container.settings().db.url)
    return container


@pytest.fixture(scope="session")
def session_maker(container):
    engine = create_engine(
        container.settings().db.url.replace("asyncpg", "psycopg2"), echo=False
    )
    session_maker = sessionmaker(engine, class_=Session, expire_on_commit=False)
    return session_maker


@pytest.fixture(scope="function")
def db_connection(session_maker):
    with session_maker() as session:
        yield session
        session.commit()


@pytest.fixture(scope="session")
def redis_client(container) -> Redis:
    client = redis.from_url(container.settings().redis.redis_url)
    return client


# должно быть session, а не module(class), иначе возникают конфликты с ивент лупом
@pytest.fixture(scope="session")
def test_client(container: Container) -> Generator[TestClient, Any, None]:
    with TestClient(create_app(container)) as client:
        yield client