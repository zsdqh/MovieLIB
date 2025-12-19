from dependency_injector import containers, providers

from backend.src.core.config import Settings
from backend.src.films.infrastructure.multiple_tokens_getter import MultipleTokensGetter
from backend.src.films.infrastructure.poiskkino_uow import PoiskkinoUnitOfWork


class Container(containers.DeclarativeContainer):
    """Контейнер для инъекции зависимостей"""

    settings = providers.Singleton(Settings)
    client = providers.Singleton(
        MultipleTokensGetter,
        base_url=settings.provided.base_url,
        tokens=settings.provided.tokens,
        timeout=5,
    )
    poiskkino_uow = providers.Singleton(PoiskkinoUnitOfWork, client)
