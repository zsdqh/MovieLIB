from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.src.core.container import Container
from backend.src.users.application.rating.get_rating_destribution import (
    RatingDestributionUseCase,
)
from backend.src.users.application.rating.remove_rating import RemoveRatingUseCase
from backend.src.users.application.rating.set_rating import SetRatingUseCase
from backend.src.users.domain.dtos import UserRatingRemoveDTO, UserRatingSetDTO
from backend.src.users.domain.interfaces.uow.rating_uow import IRatingUnitOfWork

rating_api_router = APIRouter(tags=["Ratings"])
rating_uow_annotation = Annotated[
    IRatingUnitOfWork, Depends(Provide[Container.rating_uow])
]


@rating_api_router.get("/rating/movie")
@inject
async def get_my_movie_rating(
    request: Request,
    uow: rating_uow_annotation,
    movie_id: int = Query(..., description="Идентификатор фильма"),
) -> JSONResponse:
    """Текущая оценка пользователя для фильма (или null)."""
    if not request.state.user:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    async with uow:
        rating = await uow.ratings.get_user_rating(request.state.user.sub, movie_id)
    return JSONResponse(content={"rating": rating})


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


@rating_api_router.get("/rating/destribution")
@inject
async def get_user_rating_destribution(
    request: Request, uow: rating_uow_annotation
) -> JSONResponse:
    """Распределение выставленных пользователем оценок фильмам."""
    destribution = await RatingDestributionUseCase(uow)(request.state.user)
    return JSONResponse(content=destribution)
