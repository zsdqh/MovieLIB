import json
import uuid
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.src.auth.auth.presentation.utils.custom_redirect import custom_redirect
from backend.src.auth.auth.presentation.utils.form_to_pydantic import form_to_pydantic
from backend.src.core.config import Settings
from backend.src.core.container import Container
from backend.src.files.domain.interfaces.name_generator import INameGenerator
from backend.src.files.domain.interfaces.s3_worker import IS3Worker
from backend.src.films.presentation.api import templates_annotation
from backend.src.users.application.user.user_delete_profile import (
    DeleteUserProfileUseCase,
)
from backend.src.users.application.user.user_get_by_name import GetUserByNameUseCase
from backend.src.users.application.user.user_get_info import (
    GetUserInfoUseCase,
)
from backend.src.users.application.user.user_register import (
    UserRegisterUseCase,
)
from backend.src.users.application.user.user_update_profile import (
    UpdateUserProfileUseCase,
)
from backend.src.users.domain.dtos import (
    UserRegisterDTO,
    UserUpdateDTO,
)
from backend.src.users.domain.entities import User, UserPublic
from backend.src.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork
from backend.src.users.presentation.lists_api import list_uow_annotation

user_api_router = APIRouter(tags=["Users"])
user_uow_annotation = Annotated[IUserUnitOfWork, Depends(Provide[Container.user_uow])]
pwd_hasher_annotation = Annotated[
    IPasswordHasher, Depends(Provide[Container.password_hasher])
]
s3_worker_annotation = Annotated[IS3Worker, Depends(Provide[Container.s3_worker])]
name_generator_annotation = Annotated[
    INameGenerator, Depends(Provide[Container.name_generator])
]
settings_annotation = Annotated[Settings, Depends(Provide[Container.settings])]


def _user_public_profile_for_viewer(
    u: User, viewer_sub: uuid.UUID
) -> tuple[UserPublic, bool]:
    """Публичное представление пользователя и признак «свой профиль»."""
    is_self = viewer_sub == u.id
    lists_for_view = (
        u.user_lists if is_self else [lst for lst in u.user_lists if lst.is_public]
    )
    profile = UserPublic(
        id=u.id,
        email=u.email,
        username=u.username,
        created_at=u.created_at,
        avatar_url=u.avatar_url,
        is_activated=u.is_activated,
        is_blocked=False,
        is_admin=u.is_admin,
        user_lists=lists_for_view,
    )
    return profile, is_self


def _wants_json_response(request: Request) -> bool:
    """Отправка json вместо html если указано в заголовках"""
    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return True
    return request.query_params.get("format") == "json"


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
    list_uow: list_uow_annotation,
    settings: settings_annotation,
) -> Response:
    """Регистрация нового пользователя"""
    register_data = await form_to_pydantic(request, UserRegisterDTO)

    await UserRegisterUseCase(uow=uow, pwd_hasher=pwd_hasher, list_uow=list_uow)(
        user_data=register_data, default_lists=settings.default_lists
    )
    return custom_redirect(response, "/login")


# @user_api_router.get("/users", response_model=list[UserPublic])
# @inject
# async def user_list(
#     request: Request,
#     query: Annotated[ListOfUsersParams, Query()],
#     uow: user_uow_annotation,
# ) -> Iterable[User]:
#     """Список пользователей по заданным параметрам"""
#     return await UserListUseCase(uow=uow)(
#         list_conditions=query, user_data=request.state.user
#     )


# @user_api_router.get("/block/{username}", response_model=UserPublic)
# @inject
# async def block(username: str, uow: user_uow_annotation, request: Request) -> User:
#     """Блокировка пользователя"""
#     return await UserBlockUseCase(uow=uow)(
#         username=username, new_status=True, user_data=request.state.user
#     )


# @user_api_router.get("/unblock/{username}", response_model=UserPublic)
# @inject
# async def unblock(username: str, uow: user_uow_annotation, request: Request) -> User:
#     """Разблокировка пользователя"""
#     return await UserBlockUseCase(uow=uow)(
#         username=username, new_status=False, user_data=request.state.user
#     )


@user_api_router.get("/me")
@inject
async def user_profile(
    request: Request, uow: user_uow_annotation, templates: templates_annotation
) -> Response:
    """Страница личного кабинета (редактирование, списки, аватар)."""
    u = await GetUserInfoUseCase(uow=uow)(
        user_data=request.state.user, user_id=request.state.user.sub
    )
    user_lists_json = json.dumps([lst.model_dump(mode="json") for lst in u.user_lists])
    return templates.TemplateResponse(
        request=request,
        name="me.html",
        context={"user": u, "user_lists_json": user_lists_json},
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
async def delete_user_profile(
    request: Request, uow: user_uow_annotation, response: Response
) -> Response:
    """Удаление текущего аккаунта"""
    await DeleteUserProfileUseCase(uow=uow)(user_data=request.state.user)
    return custom_redirect(response, "/logout")


@user_api_router.get("/users/{user_id}")
@inject
async def get_user_info(
    request: Request,
    uow: user_uow_annotation,
    templates: templates_annotation,
    user_id: uuid.UUID,
) -> Response:
    """Просмотр профиля: HTML-страница или JSON"""
    u = await GetUserInfoUseCase(uow=uow)(user_data=request.state.user, user_id=user_id)
    profile, is_self = _user_public_profile_for_viewer(u, request.state.user.sub)
    if _wants_json_response(request):
        return JSONResponse(content=profile.model_dump(mode="json"))
    profile_lists_json = json.dumps(
        [lst.model_dump(mode="json") for lst in profile.user_lists]
    )
    return templates.TemplateResponse(
        request=request,
        name="user_profile.html",
        context={
            "profile": profile,
            "is_self": is_self,
            "profile_lists_json": profile_lists_json,
        },
    )


@user_api_router.get("/user/{username}")
@inject
async def get_user_by_username(
    response: Response, username: str, uow: user_uow_annotation
) -> Response:
    """
    Получение данных о пользователе по имени
    на данный момент просто редирект на /user/{user_id}
    """
    user_data = await GetUserByNameUseCase(uow)(username)
    return custom_redirect(response, f"/users/{user_data.id}")


# @user_api_router.patch("/users/{username}", response_model=UserPublic)
# @inject
# async def change_role(
#     request: Request, uow: user_uow_annotation, username: str, is_admin: bool
# ) -> User:
#     """Изменение роли пользователя"""
#     return await ChangeRoleUseCase(uow=uow)(
#         user_data=request.state.user, username=username, is_admin=is_admin
#     )
