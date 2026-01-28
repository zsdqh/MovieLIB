from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, File
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.presentation.utils.custom_redirect import custom_redirect
from backend.src.files.application.delete_file import DeleteFileUseCase
from backend.src.files.application.upload_avatar import UploadAvatarUseCase
from backend.src.users.application.use_cases.users.user_add_avatar import (
    AddAvatarUseCase,
)
from backend.src.users.application.use_cases.users.user_remove_avatar import (
    RemoveAvatarUseCase,
)
from backend.src.users.presentation.users_api import (
    name_generator_annotation,
    s3_worker_annotation,
    user_uow_annotation,
)

file_router = APIRouter()


@file_router.post("/me/avatar")
@inject
async def add_avatar(
    request: Request,
    response: Response,
    uow: user_uow_annotation,
    file_worker: s3_worker_annotation,
    name_generator: name_generator_annotation,
    file: Annotated[bytes, File()],
) -> Response:
    """Установка аватара пользователя"""
    user_data = request.state.user
    file_url = await UploadAvatarUseCase(file_worker, name_generator)(file, user_data)
    await AddAvatarUseCase(uow)(request.state.user, file_url)
    return custom_redirect(response, "/refresh")


@file_router.delete("/me/avatar")
@inject
async def remove_avatar(
    request: Request,
    response: Response,
    uow: user_uow_annotation,
    file_worker: s3_worker_annotation,
) -> Response:
    """Установка аватара пользователя"""
    avatar = await RemoveAvatarUseCase(uow)(request.state.user)
    if avatar:
        await DeleteFileUseCase(file_worker)(avatar, True)
    return custom_redirect(response, "/refresh")
