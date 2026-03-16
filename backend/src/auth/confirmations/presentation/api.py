from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends, Query
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.presentation.utils.custom_redirect import custom_redirect
from backend.src.auth.confirmations.application.change_password import (
    ChangePasswordUseCase,
)
from backend.src.auth.confirmations.application.confirm_email import ConfirmEmailUseCase
from backend.src.auth.confirmations.application.send_email_confirmation import (
    SendEmailConfirmationUseCase,
)
from backend.src.auth.confirmations.application.send_password_confirmation import (
    SendPasswordConfirmationUseCase,
)
from backend.src.auth.confirmations.domain.entities import (
    Confirmation,
    ConfPublic,
    NewPassword,
)
from backend.src.auth.confirmations.domain.interfaces.code_generator import (
    ICodeGenerator,
)
from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.auth.confirmations.domain.interfaces.conf_uow import IConfUnitOfWork
from backend.src.auth.confirmations.domain.interfaces.email_sender import IEmailSender
from backend.src.core.container import Container
from backend.src.users.domain.entities import User, UserPublic
from backend.src.users.presentation.users_api import (
    pwd_hasher_annotation,
    user_uow_annotation,
)

conf_api_router = APIRouter(tags=["Confirmations"])
conf_uow_annotation = Annotated[IConfUnitOfWork, Depends(Provide[Container.conf_uow])]
sender_annotation = Annotated[IEmailSender, Depends(Provide[Container.email_sender])]
generator_annotation = Annotated[
    ICodeGenerator, Depends(Provide[Container.code_generator])
]
cache_repository_annotation = Annotated[
    IConfRepository, Depends(Provide[Container.conf_repository])
]


@conf_api_router.get("/send_confirmation", response_model=ConfPublic)
@inject
async def send_email_confirmation(
    request: Request,
    uow: conf_uow_annotation,
    sender: sender_annotation,
    generator: generator_annotation,
) -> Confirmation:
    """Отправка токена для подтверждения почты"""
    return await SendEmailConfirmationUseCase(
        uow=uow, sender=sender, generator=generator
    )(user_data=request.state.user)


@conf_api_router.get("/confirm_email", response_model=UserPublic)
@inject
async def confirm_email(
    request: Request,
    response: Response,
    code: Annotated[str, Query()],
    conf_uow: conf_uow_annotation,
    user_uow: user_uow_annotation,
) -> Response:
    """Подтверждение почты с помощью полученного кода подтверждения"""
    await ConfirmEmailUseCase(conf_uow=conf_uow, user_uow=user_uow)(
        user_data=request.state.user, code=code
    )
    return custom_redirect(response, "/refresh")


@conf_api_router.get("/send_password_confirmation", response_model=ConfPublic)
@inject
async def send_password_confirmation(
    request: Request,
    sender: sender_annotation,
    generator: generator_annotation,
    cache_repository: cache_repository_annotation,
    uow: conf_uow_annotation,
) -> Confirmation:
    """Подтверждение сброса пароля"""
    return await SendPasswordConfirmationUseCase(
        cache_repository=cache_repository, uow=uow, generator=generator, sender=sender
    )(request.state.user)


@conf_api_router.post("/change_password", response_model=UserPublic)
@inject
async def change_password(
    request: Request,
    cache_repository: cache_repository_annotation,
    code: Annotated[str, Query()],
    new_password: NewPassword,
    pwd_hasher: pwd_hasher_annotation,
    uow: user_uow_annotation,
) -> User:
    """Изменение пароля с подтверждением из почты"""
    return await ChangePasswordUseCase(
        cache_repository=cache_repository, pwd_hasher=pwd_hasher, uow=uow
    )(request.state.user, code, new_password)
