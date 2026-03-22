from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from backend.src.core.container import Container
from backend.src.films.application.get_by_name import GetMoviesByNameUseCase
from backend.src.films.application.get_filtered_movies import GetFilteredMoviesUseCase
from backend.src.films.application.get_initial_page import GetInitialPageUseCase
from backend.src.films.application.get_movie_use_case import GetMovieUseCase
from backend.src.films.application.get_person_use_case import GetPersonUseCase
from backend.src.films.domain.entities.filters import (
    FilmParams,
    parse_genre_with_priority,
    parse_movie_type_with_priority,
)
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork
from backend.src.films.domain.interfaces.get_person_uow import IGetPersonUnitOfWork
from backend.src.films.domain.interfaces.movie_uow import IMovieUnitOfWork

films_router = APIRouter(tags=["Movies"])
templates_annotation = Annotated[Jinja2Templates, Depends(Provide[Container.templates])]
poiskkino_film_uow_annotation = Annotated[
    IGetMovieUnitOfWork, Depends(Provide[Container.poiskkino_film_uow])
]
db_get_film_uow_annotation = Annotated[
    IGetMovieUnitOfWork, Depends(Provide[Container.db_get_film_uow])
]
db_get_person_uow_annotation = Annotated[
    IGetPersonUnitOfWork, Depends(Provide[Container.db_get_person_uow])
]
db_movie_annotation = Annotated[
    IMovieUnitOfWork, Depends(Provide[Container.db_film_uow])
]
poiskkino_person_uow_annotation = Annotated[
    IGetPersonUnitOfWork, Depends(Provide[Container.poiskkono_person_uow])
]


@films_router.get("/")
@inject
async def index(
    request: Request,
    templates: templates_annotation,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
    page: int = 1,
) -> Response:
    """Главная страница"""
    movies = await GetInitialPageUseCase(external_uow, internal_uow, db_uow)(page)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": request.state.user, "movies": movies},
    )


@films_router.get("/movie/{movie_id}/")
@inject
async def get_film_page(
    request: Request,
    templates: templates_annotation,
    movie_id: int,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
) -> Response:
    """Открытие страницы фильма по id"""
    movie_data = await GetMovieUseCase(external_uow, internal_uow, db_uow)(movie_id)
    return templates.TemplateResponse(
        request=request, name="film.html", context={"movie": movie_data}
    )


@films_router.get("/person/{person_id}/")
@inject
async def get_person_page(
    request: Request,
    templates: templates_annotation,
    person_id: int,
    external_uow: poiskkino_person_uow_annotation,
    internal_uow: db_get_person_uow_annotation,
    db_uow: db_movie_annotation,
) -> Response:
    """Открытие страницы фильма по id"""
    person_data = await GetPersonUseCase(external_uow, internal_uow, db_uow)(person_id)
    return templates.TemplateResponse(
        request=request, name="person.html", context={"person": person_data}
    )


@films_router.get("/search")
@inject
async def search_by_name(
    request: Request,
    templates: templates_annotation,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
    query: str,
    page: int = 1,
) -> Response:
    """Главная страница"""
    movies = await GetMoviesByNameUseCase(external_uow, internal_uow, db_uow)(
        query, page
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": request.state.user, "movies": movies},
    )


@films_router.get("/filter")
@inject
async def search_with_filters(
    request: Request,
    templates: templates_annotation,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
    page: int = 1,
    params: FilmParams = Depends(),
    genres: list[str] = Query(None, alias="genres"),
    type_number: list[str] = Query(None, alias="type_number"),
) -> Response:
    """Получение фильмов с указанными параметрами"""
    params = FilmParams(
        **params.model_dump(exclude={"type_number", "genres"}),
        type_number=(
            [parse_movie_type_with_priority(num) for num in type_number]
            if type_number
            else None
        ),
        genres=(
            [parse_genre_with_priority(genre) for genre in genres] if genres else None
        ),
    )

    movies = await GetFilteredMoviesUseCase(external_uow, internal_uow, db_uow)(
        params, page
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": request.state.user, "movies": movies},
    )
