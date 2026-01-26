from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from backend.src.core.container import Container
from backend.src.films.domain.interfaces.get_film_uow import IGetFilmUnitOfWork

films_router = APIRouter()
templates_annotation = Annotated[Jinja2Templates, Depends(Provide[Container.templates])]
poiskkino_uow_annotation = Annotated[
    IGetFilmUnitOfWork, Depends(Provide[Container.poiskkino_uow])
]


@films_router.get("/")
@inject
async def index(request: Request, templates: templates_annotation) -> Response:
    """Главная страница"""
    return templates.TemplateResponse(
        request=request, name="base.html", context={"user": request.state.user}
    )


@films_router.get("/movie/{movie_id}")
@inject
async def get_film_page(
    request: Request,
    templates: templates_annotation,
    movie_id: int,
    external_uow: poiskkino_uow_annotation,
) -> Response:
    """Открытие страницы фильма по id"""
    async with external_uow as uow:
        movie_data = await uow.films.get_film_by_id(movie_id)
    return templates.TemplateResponse(
        request=request, name="film.html", context={"movie": movie_data}
    )
