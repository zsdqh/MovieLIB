import redis.asyncio as redis
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.auth.auth.infrastructure.jwt_provider import JWTProvider
from backend.src.auth.auth.infrastructure.jwt_worker import JWTWorker
from backend.src.auth.auth.infrastructure.transport.cookie_transport import (
    CookieTransport,
)
from backend.src.auth.auth.infrastructure.transport.header_transport import (
    HeaderTransport,
)
from backend.src.auth.confirmations.infrastructure.db.pg_conf_uow import (
    PGConfUnitOfWork,
)
from backend.src.auth.confirmations.infrastructure.redis_conf_repository import (
    RedisConfRepository,
)
from backend.src.auth.confirmations.infrastructure.services.email_sender import (
    SESCustomClient,
)
from backend.src.auth.confirmations.infrastructure.services.generator import (
    CodeGenerator,
)
from backend.src.auth.users.infrastructure.db.units_of_work.user_uow import (
    PGUserUnitOfWork,
)
from backend.src.auth.users.infrastructure.services.avatar_worker import AvatarWorker
from backend.src.auth.users.infrastructure.services.password_hasher import (
    PasswordHasher,
)
from backend.src.core.config import Settings
from backend.src.films.infrastructure.multiple_tokens_getter import MultipleTokensGetter
from backend.src.films.infrastructure.poiskkino_uow import PoiskkinoUnitOfWork


class Container(containers.DeclarativeContainer):
    """Контейнер для инъекции зависимостей"""

    # --- BASE

    wiring_config = containers.WiringConfiguration(packages=("backend.src",))
    settings = providers.Singleton(Settings)

    # --- poiskkino.dev

    client = providers.Singleton(
        MultipleTokensGetter,
        base_url=settings.provided.base_url,
        tokens=settings.provided.tokens,
        timeout=5,
    )
    poiskkino_uow = providers.Singleton(PoiskkinoUnitOfWork, client)

    # --- auth

    password_hasher = providers.Singleton(PasswordHasher)
    token_provider = providers.Singleton(JWTProvider, config=settings.provided.auth)
    header_transport = providers.Factory(
        HeaderTransport, header_name="Authorization", token_type_prefix="Bearer"
    )

    cookie_transport = providers.Factory(
        CookieTransport,
        cookie_name="refresh_token",
        cookie_max_age=settings.provided.auth.refresh_ttl,
    )

    token_worker = providers.Factory(
        JWTWorker,
        token_provider=token_provider,
        access_transport=header_transport,
        refresh_transport=cookie_transport,
    )

    email_sender = providers.Singleton(
        SESCustomClient, settings.provided.email, settings.provided.aws
    )

    code_generator = providers.Singleton(CodeGenerator)

    redis_client = providers.Singleton(
        redis.from_url,
        url=settings.provided.redis.redis_url,
        decode_responses=True,
        encoding="utf-8",
    )
    conf_repository = providers.Singleton(
        RedisConfRepository,
        redis_client=redis_client,
        code_ttl=settings.provided.redis.code_ttl,
    )

    avatar_worker = providers.Singleton(
        AvatarWorker, settings.provided.file_service_url
    )

    # --- DB

    engine = providers.Singleton(
        create_async_engine,
        settings.provided.db.url,
        echo=True,
    )

    async_session_maker = providers.Singleton(
        async_sessionmaker, engine, class_=AsyncSession, expire_on_commit=False
    )

    user_uow = providers.Factory(PGUserUnitOfWork, async_session_maker)
    conf_uow = providers.Factory(PGConfUnitOfWork, async_session_maker)
