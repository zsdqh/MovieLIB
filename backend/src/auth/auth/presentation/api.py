from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.application.login import LoginUseCase
from backend.src.auth.auth.application.logout import LogoutUseCase
from backend.src.auth.auth.application.refresh import RefreshUseCase
from backend.src.auth.auth.domain.dtos import LoginDTO
from backend.src.auth.auth.infrastructure.jwt_worker import JWTWorker
from backend.src.auth.auth.presentation.utils.custom_redirect import custom_redirect
from backend.src.auth.auth.presentation.utils.form_to_pydantic import form_to_pydantic
from backend.src.auth.users.domain.entities import User, UserPublic
from backend.src.auth.users.domain.interfaces.password_hasher import IPasswordHasher
from backend.src.auth.users.presentation.users_api import user_uow_annotation
from backend.src.core.container import Container
from backend.src.films.presentation.api import templates_annotation

jwt_api_router = APIRouter()
token_worker_annotation = Annotated[JWTWorker, Depends(Provide[Container.token_worker])]


@jwt_api_router.get("/login")
@inject
async def login_page(request: Request, templates: templates_annotation) -> Response:
    """Открытие страницы входа в аккаунт"""
    return templates.TemplateResponse(request=request, name="login.html", context={})


@jwt_api_router.post("/login")
@inject
async def login(
    request: Request,
    response: Response,
    uow: user_uow_annotation,
    token_worker: token_worker_annotation,
    pwd_hasher: Annotated[IPasswordHasher, Depends(Provide[Container.password_hasher])],
) -> Response:
    """Вход пользователя в аккаунт с выдачей access и refresh токенов"""
    token_worker.access_transport.set_request_response(request, response)
    token_worker.refresh_transport.set_request_response(request, response)

    login_data = await form_to_pydantic(request, LoginDTO)

    await LoginUseCase(uow=uow, token_worker=token_worker, pwd_hasher=pwd_hasher)(
        login_data=login_data
    )
    return custom_redirect(response, "/me")


@jwt_api_router.get("/refresh", response_model=UserPublic)
@inject
async def refresh(
    request: Request,
    response: Response,
    token_worker: token_worker_annotation,
    uow: user_uow_annotation,
) -> User:
    """Обновление access токена, используя refresh токен"""
    token_worker.access_transport.set_request_response(request, response)
    token_worker.refresh_transport.set_request_response(request, response)

    return await RefreshUseCase(token_worker=token_worker, uow=uow)(
        user_data=request.state.user
    )


@jwt_api_router.get("/logout")
@inject
async def logout(
    request: Request,
    response: Response,
    token_worker: token_worker_annotation,
    uow: user_uow_annotation,
) -> None:
    """Выход из аккаунта (завершение сессии)"""
    token_worker.access_transport.set_response(response)
    token_worker.refresh_transport.set_response(response)

    return await LogoutUseCase(token_worker=token_worker, uow=uow)(
        user_data=request.state.user
    )
