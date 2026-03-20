from typing import Annotated, Iterable

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends, Query
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.presentation.utils.custom_redirect import custom_redirect
from backend.src.auth.auth.presentation.utils.form_to_pydantic import form_to_pydantic
from backend.src.core.container import Container
from backend.src.files.domain.interfaces.name_generator import INameGenerator
from backend.src.files.domain.interfaces.s3_worker import IS3Worker
from backend.src.films.presentation.api import templates_annotation
from backend.src.users.application.user.user_block import (
    UserBlockUseCase,
)
from backend.src.users.application.user.user_change_role import (
    ChangeRoleUseCase,
)
from backend.src.users.application.user.user_delete_profile import (
    DeleteUserProfileUseCase,
)
from backend.src.users.application.user.user_get_info import (
    GetUserInfoUseCase,
)
from backend.src.users.application.user.user_list import UserListUseCase
from backend.src.users.application.user.user_profile import (
    UserProfileUseCase,
)
from backend.src.users.application.user.user_register import (
    UserRegisterUseCase,
)
from backend.src.users.application.user.user_update_profile import (
    UpdateUserProfileUseCase,
)
from backend.src.users.domain.dtos import (
    ListOfUsersParams,
    UserRegisterDTO,
    UserUpdateDTO,
)
from backend.src.users.domain.entities import User, UserPublic
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork

user_api_router = APIRouter(tags=["Users"])
user_uow_annotation = Annotated[IUserUnitOfWork, Depends(Provide[Container.user_uow])]
pwd_hasher_annotation = Annotated[
    IPasswordHasher, Depends(Provide[Container.password_hasher])
]
s3_worker_annotation = Annotated[IS3Worker, Depends(Provide[Container.s3_worker])]
name_generator_annotation = Annotated[
    INameGenerator, Depends(Provide[Container.name_generator])
]


@user_api_router.get("/register")
@inject
async def register_page(request: Request, templates: templates_annotation) -> Response:
    """Регистрация нового пользователя"""
    return templates.TemplateResponse(request=request, name="register.html", context={})


@user_api_router.post("/register")
@inject
async def register(
    request: Request,
    response: Response,
    pwd_hasher: pwd_hasher_annotation,
    uow: user_uow_annotation,
) -> Response:
    """Регистрация нового пользователя"""
    register_data = await form_to_pydantic(request, UserRegisterDTO)

    await UserRegisterUseCase(uow=uow, pwd_hasher=pwd_hasher)(user_data=register_data)
    return custom_redirect(response, "/login")


@user_api_router.get("/users", response_model=list[UserPublic])
@inject
async def user_list(
    request: Request,
    query: Annotated[ListOfUsersParams, Query()],
    uow: user_uow_annotation,
) -> Iterable[User]:
    """Список пользователей по заданным параметрам"""
    return await UserListUseCase(uow=uow)(
        list_conditions=query, user_data=request.state.user
    )


@user_api_router.get("/block/{username}", response_model=UserPublic)
@inject
async def block(username: str, uow: user_uow_annotation, request: Request) -> User:
    """Блокировка пользователя"""
    return await UserBlockUseCase(uow=uow)(
        username=username, new_status=True, user_data=request.state.user
    )


@user_api_router.get("/unblock/{username}", response_model=UserPublic)
@inject
async def unblock(username: str, uow: user_uow_annotation, request: Request) -> User:
    """Разблокировка пользователя"""
    return await UserBlockUseCase(uow=uow)(
        username=username, new_status=False, user_data=request.state.user
    )


@user_api_router.get("/me")
@inject
async def user_profile(
    request: Request, uow: user_uow_annotation, templates: templates_annotation
) -> Response:
    """Данные о текущем пользователя"""
    user_data = await UserProfileUseCase(uow=uow)(user_data=request.state.user)
    return templates.TemplateResponse(
        request=request, name="me.html", context={"user": user_data}
    )


@user_api_router.patch("/me", response_model=UserPublic)
@inject
async def update_user_profile(
    request: Request, uow: user_uow_annotation, update_data: UserUpdateDTO
) -> User:
    """Изменение текущего аккаунта"""
    return await UpdateUserProfileUseCase(uow=uow)(
        user_data=request.state.user, update_data=update_data
    )


@user_api_router.delete("/me")
@inject
async def delete_user_profile(request: Request, uow: user_uow_annotation) -> None:
    """Удаление текущего аккаунта"""
    return await DeleteUserProfileUseCase(uow=uow)(user_data=request.state.user)


@user_api_router.get("/users/{username}", response_model=UserPublic)
@inject
async def get_user_info(
    request: Request, uow: user_uow_annotation, username: str
) -> User:
    """Получение информации о пользователе"""
    return await GetUserInfoUseCase(uow=uow)(
        user_data=request.state.user, username=username
    )


@user_api_router.patch("/users/{username}", response_model=UserPublic)
@inject
async def change_role(
    request: Request, uow: user_uow_annotation, username: str, is_admin: bool
) -> User:
    """Изменение роли пользователя"""
    return await ChangeRoleUseCase(uow=uow)(
        user_data=request.state.user, username=username, is_admin=is_admin
    )
