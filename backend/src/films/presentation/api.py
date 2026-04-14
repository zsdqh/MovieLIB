import json
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from backend.src.core.container import Container
from backend.src.films.application.get_by_name import GetMoviesByNameUseCase
from backend.src.films.application.get_filtered_movies import GetFilteredMoviesUseCase
from backend.src.films.application.get_initial_page import GetInitialPageUseCase
from backend.src.films.application.get_movie_use_case import GetMovieUseCase
from backend.src.films.application.get_person_use_case import GetPersonUseCase
from backend.src.films.application.get_random_film import GetRandomFilmUseCase
from backend.src.films.domain.entities.constants import Genre, MovieType, OrderableField
from backend.src.films.domain.entities.entities import Movie
from backend.src.films.domain.entities.filters import (
    FilmParams,
    FilterWithPriority,
    RandomParams,
    parse_genre_with_priority,
    parse_movie_type_with_priority,
    parse_order_field,
)
from backend.src.films.domain.interfaces.get_movie_uow import IGetMovieUnitOfWork
from backend.src.films.domain.interfaces.get_person_uow import IGetPersonUnitOfWork
from backend.src.films.domain.interfaces.movie_uow import IMovieUnitOfWork
from backend.src.users.application.user.user_get_info import GetUserInfoUseCase
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork

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
user_uow_annotation = Annotated[IUserUnitOfWork, Depends(Provide[Container.user_uow])]


def _wants_json(request: Request) -> bool:
    """Проверка на то, требуется ли json формат или нет"""
    accept = request.headers.get("accept", "")
    return "application/json" in accept


def _movies_json_response(
    movies: list[Movie],
    page: int,
    *,
    query: str | None = None,
) -> JSONResponse:
    """Преобразование фильмов в json формат"""
    content: dict[str, Any] = {
        "movies": [m.model_dump(mode="json") for m in movies],
        "page": page,
    }
    if query is not None:
        content["query"] = query
    return JSONResponse(content=content)


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
    """
    Главная страница: начальный список фильмов и
    поиск по названию (переход на /search).
    """
    movies = await GetInitialPageUseCase(external_uow, internal_uow, db_uow)(page)
    if _wants_json(request):
        return _movies_json_response(movies, page)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": request.state.user,
            "movies": movies,
            "page": page,
            "is_search": False,
        },
    )


@films_router.get("/movie/{movie_id}/comments-page")
@inject
async def film_comments_page(
    request: Request,
    templates: templates_annotation,
    movie_id: int,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
) -> Response:
    """HTML-страница комментариев к фильму (данные подгружаются через API)."""
    movie_data = await GetMovieUseCase(external_uow, internal_uow, db_uow)(movie_id)
    return templates.TemplateResponse(
        request=request,
        name="film_comments.html",
        context={"movie": movie_data, "user": request.state.user},
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
    user_uow: user_uow_annotation,
) -> Response:
    """Открытие страницы фильма по id"""
    movie_data = await GetMovieUseCase(external_uow, internal_uow, db_uow)(movie_id)
    user_lists_json = "[]"
    if request.state.user:
        u = await GetUserInfoUseCase(user_uow)(
            request.state.user, request.state.user.sub
        )
        user_lists_json = json.dumps(
            [lst.model_dump(mode="json") for lst in u.user_lists]
        )
    return templates.TemplateResponse(
        request=request,
        name="film.html",
        context={
            "movie": movie_data,
            "user_lists_json": user_lists_json,
            "user": request.state.user,
        },
    )


@films_router.post("/movie/{movie_id}/refresh")
@inject
async def refresh_movie_from_external_api(
    movie_id: int,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
) -> JSONResponse:
    """Перезагрузка данных о фильме из внешнего API и сохранение в БД."""
    movie = await GetMovieUseCase(external_uow, internal_uow, db_uow)(movie_id, True)
    return JSONResponse(content=movie.model_dump(mode="json"))


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
        request=request,
        name="person.html",
        context={"person": person_data, "user": request.state.user},
    )


@films_router.post("/person/{person_id}/refresh")
@inject
async def refresh_person_from_external_api(
    person_id: int,
    external_uow: poiskkino_person_uow_annotation,
    internal_uow: db_get_person_uow_annotation,
    db_uow: db_movie_annotation,
) -> JSONResponse:
    """Перезагрузка данных о персоне из внешнего API и сохранение в БД."""
    person = await GetPersonUseCase(external_uow, internal_uow, db_uow)(person_id, True)
    return JSONResponse(content=person.model_dump(mode="json"))


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
    if _wants_json(request):
        return _movies_json_response(movies, page, query=query)
    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "user": request.state.user,
            "movies": movies,
            "page": page,
            "query": query,
        },
    )


@films_router.get("/filters")
@inject
async def filters_form_page(
    request: Request,
    templates: templates_annotation,
) -> Response:
    """Страница редактирования параметров FilmParams перед запросом к /filter."""
    return templates.TemplateResponse(
        request=request,
        name="filters.html",
        context={
            "user": request.state.user,
            "genre_list": list(Genre),
            "movie_type_list": list(
                filter(lambda x: x != MovieType.REMAKE, list(MovieType))
            ),
            "sort_fields": OrderableField.ru_fields(),
        },
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
    order_by: list[str] = Query(None, alias="order_by"),
    type_number: list[str] = Query(None, alias="type_number"),
) -> Response:
    """Получение фильмов с указанными параметрами"""
    params = FilmParams(
        **params.model_dump(exclude={"type_number", "genres", "sort_fields"}),
        type_number=parse_types(type_number),
        genres=parse_genres(genres),
        sort_fields=[parse_order_field(s) for s in (order_by if order_by else [])],
    )

    movies = await GetFilteredMoviesUseCase(external_uow, internal_uow, db_uow)(
        params, page
    )
    if _wants_json(request):
        return _movies_json_response(movies, page)
    return templates.TemplateResponse(
        request=request,
        name="filter_results.html",
        context={"user": request.state.user, "movies": movies, "page": page},
    )


@films_router.get("/random/params")
@films_router.get("/random/filters")
@inject
async def random_filters_form_page(
    request: Request,
    templates: templates_annotation,
) -> Response:
    """Страница редактирования параметров RandomParams перед запросом к /random."""
    return templates.TemplateResponse(
        request=request,
        name="random_filters.html",
        context={
            "user": request.state.user,
            "genre_list": list(Genre),
            "movie_type_list": list(
                filter(lambda x: x != MovieType.REMAKE, list(MovieType))
            ),
        },
    )


@films_router.get("/random")
@inject
async def get_random_film(
    request: Request,
    templates: templates_annotation,
    external_uow: poiskkino_film_uow_annotation,
    internal_uow: db_get_film_uow_annotation,
    db_uow: db_movie_annotation,
    params: RandomParams = Depends(),
    genres: list[str] = Query(None, alias="genres"),
    type_number: list[str] = Query(None, alias="type_number"),
) -> Response:
    """Получение случайного фильма по параметрам RandomParams."""
    random_params = RandomParams(
        **params.model_dump(exclude={"type_number", "genres"}),
        type_number=parse_types(type_number),
        genres=parse_genres(genres),
    )

    movie = await GetRandomFilmUseCase(external_uow, internal_uow, db_uow)(
        random_params
    )

    if _wants_json(request):
        return JSONResponse(
            content={"movie": movie.model_dump(mode="json") if movie else None}
        )

    query_string = request.url.query
    return templates.TemplateResponse(
        request=request,
        name="random_result.html",
        context={
            "user": request.state.user,
            "movie": movie,
            "query_string": query_string,
        },
    )


def parse_types(type_number: list[str] | None) -> list[FilterWithPriority] | None:
    """Преобразование списка типов для поиска"""
    return (
        [parse_movie_type_with_priority(num) for num in type_number]
        if type_number
        else None
    )


def parse_genres(genres: list[str] | None) -> list[FilterWithPriority] | None:
    """Преобразование списка жанров для поиска"""
    return [parse_genre_with_priority(genre) for genre in genres] if genres else None
