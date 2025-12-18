from dependency_injector import containers, providers

from backend.src.core.config import Settings
from backend.src.poiskkino.infrastructure.sender_with_multiple_tokens import (
    SenderWithMultipleTokens,
)


class Container(containers.DeclarativeContainer):
    """Контейнер для инъекции зависимостей"""

    settings = providers.Singleton(Settings)

    sender = providers.Singleton(
        SenderWithMultipleTokens, settings.provided.base_url, settings.provided.tokens
    )
