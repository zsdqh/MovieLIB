from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from starlette.responses import JSONResponse

from backend.src.api.v1.routes import v1_routers
from backend.src.core.container import Container
from backend.src.core.exception_handlers import register_exception_handlers


class AppWithContainer(FastAPI):
    """fastapi приложение, имеющее контейнер с зависимостями"""

    container: Container


def create_app(container: Container) -> AppWithContainer:
    """Создание fastapi приложения с переданными зависимостями"""

    @asynccontextmanager
    async def lifespan(fast_app: AppWithContainer) -> Any:
        """Действия, производимые до и после запуска fastapi приложения"""
        for route in fast_app.routes:
            print(route)
        async with container.poiskkino_uow() as uow:
            # Тест uow
            print(uow.films)
        yield

    app = AppWithContainer(default_response_class=JSONResponse, lifespan=lifespan)
    app.include_router(v1_routers)

    app.container = container

    register_exception_handlers(app)
    return app


app = create_app(Container())
