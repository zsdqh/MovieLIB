from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request

from backend.src.core.container import Container
from backend.src.users.application.rating.remove_rating import RemoveRatingUseCase
from backend.src.users.application.rating.set_rating import SetRatingUseCase
from backend.src.users.domain.dtos import UserRatingRemoveDTO, UserRatingSetDTO
from backend.src.users.domain.interfaces.rating_uow import IRatingUnitOfWork

rating_api_router = APIRouter(tags=["Ratings"])
rating_uow_annotation = Annotated[
    IRatingUnitOfWork, Depends(Provide[Container.rating_uow])
]


@rating_api_router.post("/rating/movie")
@inject
async def set_rating(
    request: Request, rating_data: UserRatingSetDTO, uow: rating_uow_annotation
) -> None:
    """Установка оценки фильма пользователем"""
    await SetRatingUseCase(uow)(rating_data, request.state.user)


@rating_api_router.delete("/rating/movie")
@inject
async def remove_rating(
    request: Request, rating_data: UserRatingRemoveDTO, uow: rating_uow_annotation
) -> None:
    """Удаление оценки фильма пользователем"""
    await RemoveRatingUseCase(uow)(rating_data.movie_id, request.state.user)
