from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from backend.src.core.container import Container

films_router = APIRouter()
templates_annotation = Annotated[Jinja2Templates, Depends(Provide[Container.templates])]


@films_router.get("/")
@inject
def index(request: Request, templates: templates_annotation) -> Response:
    """Главная страница"""
    return templates.TemplateResponse(
        request=request, name="base.html", context={"user": request.state.user}
    )
