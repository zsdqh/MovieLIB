from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request

from backend.src.core.container import Container
from backend.src.users.application.lists.add_movie import AddMovieUseCase
from backend.src.users.application.lists.create_list import CreateListUseCase
from backend.src.users.application.lists.delete_list import DeleteListUseCase
from backend.src.users.application.lists.edit_list import EditListUseCase
from backend.src.users.application.lists.remove_movie import RemoveMovieUseCase
from backend.src.users.domain.dtos import CreateListDTO, EditListDTO, ListMovieDTO
from backend.src.users.domain.entities import UserList
from backend.src.users.domain.interfaces.uow.list_uow import IListUnitOfWork

lists_api_router = APIRouter(tags=["Ratings"])
list_uow_annotation = Annotated[IListUnitOfWork, Depends(Provide[Container.list_uow])]


@lists_api_router.post("/list")
@inject
async def create_list(
    request: Request, list_data: CreateListDTO, uow: list_uow_annotation
) -> UserList:
    """Создание пользовательского списка"""
    return await CreateListUseCase(uow)(list_data, request.state.user)


@lists_api_router.patch("/list/{list_id}")
@inject
async def edit_list(
    request: Request, list_data: EditListDTO, list_id: int, uow: list_uow_annotation
) -> UserList:
    """Изменение данных о пользовательском списке"""
    return await EditListUseCase(uow)(list_id, request.state.user, list_data)


@lists_api_router.delete("/list/{list_id}")
@inject
async def delete_list(request: Request, list_id: int, uow: list_uow_annotation) -> None:
    """Удаление пользовательского списка"""
    await DeleteListUseCase(uow)(list_id, request.state.user)


@lists_api_router.post("/list/{list_id}/movies")
@inject
async def add_movie(
    request: Request, list_id: int, list_movie: ListMovieDTO, uow: list_uow_annotation
) -> UserList:
    """Добавление фильма в пользовательский список"""
    return await AddMovieUseCase(uow)(list_id, list_movie.movie_id, request.state.user)


@lists_api_router.delete("/list/{list_id}/movies")
@inject
async def remove_movie(
    request: Request, list_id: int, list_movie: ListMovieDTO, uow: list_uow_annotation
) -> UserList:
    """Удаление фильма из пользовательского списка"""
    return await RemoveMovieUseCase(uow)(
        list_id, list_movie.movie_id, request.state.user
    )
