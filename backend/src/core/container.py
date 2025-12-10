from dependency_injector import containers, providers

from backend.src.core.config import Settings


class Container(containers.DeclarativeContainer):
    """Контейнер для инъекции зависимостей"""

    settings = providers.Singleton(Settings)
