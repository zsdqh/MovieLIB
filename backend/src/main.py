from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from backend.src.api.v1.routes import v1_routers
from backend.src.auth.auth.presentation.auth_middleware import AuthenticationMiddleware
from backend.src.auth.auth.presentation.refresh_middleware import RefreshMiddleware
from backend.src.core.container import Container
from backend.src.core.exception_handlers import register_exception_handlers

# from backend.src.auth.confirmations.presentation.middlewares
# import UserActiveMiddleware


class AppWithContainer(FastAPI):
    """fastapi приложение, имеющее контейнер с зависимостями"""

    container: Container


def create_app(container: Container) -> AppWithContainer:
    """Создание fastapi приложения с переданными зависимостями"""

    @asynccontextmanager
    async def lifespan(fast_app: AppWithContainer) -> Any:
        """Действия, производимые до и после запуска fastapi приложения"""
        await fast_app.container.email_sender().create_templates()
        await fast_app.container.s3_worker().set_bucket_policy()
        async with fast_app.container.client():
            # async with fast_app.container.poiskkino_film_uow() as uow:
            #     print(await uow.films.get_film_by_id(666))
            yield

    app = AppWithContainer(lifespan=lifespan)
    app.include_router(v1_routers)
    app.mount("/static", StaticFiles(directory="/app/frontend/static"), name="static")

    app.container = container

    # app.add_middleware(UserActiveMiddleware)  # type: ignore[arg-type]

    app.add_middleware(
        AuthenticationMiddleware,  # type: ignore[arg-type]
        jwt_worker_provider=container.token_worker,
        templates=container.templates(),
    )
    app.add_middleware(
        RefreshMiddleware,  # type: ignore[arg-type]
        jwt_worker_provider=container.token_worker,
        user_uow=container.user_uow,
    )

    register_exception_handlers(app)
    return app


app = create_app(Container())
Instrumentator().instrument(app).expose(app)
