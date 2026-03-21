import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request

from backend.src.auth.auth.presentation.utils.form_to_pydantic import form_to_pydantic
from backend.src.core.container import Container
from backend.src.users.application.comments.add_comment import AddCommentUseCase
from backend.src.users.application.comments.add_reaction import AddReactionUseCase
from backend.src.users.application.comments.delete_comment import DeleteCommentUseCase
from backend.src.users.application.comments.get_movie_comments import (
    GetMovieCommentsUseCase,
)
from backend.src.users.application.comments.get_user_comments import (
    GetUserCommentsUseCase,
)
from backend.src.users.application.comments.remove_reaction import RemoveReactionUseCase
from backend.src.users.domain.dtos import CreateCommentDTO
from backend.src.users.domain.entities import Comment, CommentPage
from backend.src.users.domain.interfaces.uow.comment_uow import ICommentUnitOfWork

comments_api_router = APIRouter(tags=["Comments"])
comment_uow_annotation = Annotated[
    ICommentUnitOfWork, Depends(Provide[Container.comment_uow])
]


@comments_api_router.get("/movie/{movie_id}/comments")
@inject
async def get_movie_comments(
    movie_id: int, page: int, uow: comment_uow_annotation
) -> CommentPage:
    """Получение комментариев о фильме с пагинацией"""
    return await GetMovieCommentsUseCase(uow)(movie_id, page)


@comments_api_router.post("/movie/{movie_id}/comments")
@inject
async def add_comment(
    request: Request,
    # create_data: CreateCommentDTO,
    movie_id: int,
    uow: comment_uow_annotation,
) -> Comment:
    """Добавление комментария к фильму"""
    create_data = await form_to_pydantic(request, CreateCommentDTO)
    return await AddCommentUseCase(uow)(create_data, movie_id, request.state.user)


@comments_api_router.delete("/comment/{comment_id}")
@inject
async def delete_comment(
    request: Request, comment_id: int, uow: comment_uow_annotation
) -> None:
    """Удаление комментария"""
    return await DeleteCommentUseCase(uow)(comment_id, request.state.user)


@comments_api_router.post("/comment/{comment_id}/like")
@inject
async def like_comment(
    request: Request, comment_id: int, uow: comment_uow_annotation
) -> Comment:
    """Лайкнуть комментарий"""
    return await AddReactionUseCase(uow)(comment_id, request.state.user, True)


@comments_api_router.post("/comment/{comment_id}/dislike")
@inject
async def dislike_comment(
    request: Request, comment_id: int, uow: comment_uow_annotation
) -> Comment:
    """Дизлайкнуть комментарий"""
    return await AddReactionUseCase(uow)(comment_id, request.state.user, False)


@comments_api_router.delete("/comment/{comment_id}/like")
@comments_api_router.delete("/comment/{comment_id}/dislike")
@inject
async def remove_reaction(
    request: Request, comment_id: int, uow: comment_uow_annotation
) -> Comment:
    """Удаление реакции на комментарий"""
    return await RemoveReactionUseCase(uow)(comment_id, request.state.user)


@comments_api_router.get("/user/{user_id}/comments")
@inject
async def get_user_comments(
    user_id: uuid.UUID, uow: comment_uow_annotation, page: int
) -> CommentPage:
    """Получений комментариев пользователя без ответов"""
    return await GetUserCommentsUseCase(uow)(user_id, page)
