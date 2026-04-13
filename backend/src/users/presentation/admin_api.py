from datetime import date
from typing import Annotated, Iterable

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from backend.src.core.container import Container
from backend.src.users.application.admin.block import BlockUserUseCase
from backend.src.users.application.admin.change_role import ChangeRoleUseCase
from backend.src.users.application.admin.get_reports import GetReportsUseCase
from backend.src.users.application.admin.solve_report import SolveReportUseCase
from backend.src.users.application.admin.unblock import UnblockUserUseCase
from backend.src.users.application.admin.user_list import UserListUseCase
from backend.src.users.domain.dtos import ListOfUsersParams
from backend.src.users.domain.entities import (
    Blocking,
    CreateBlocking,
    Report,
    User,
    UserPublic,
)
from backend.src.users.domain.interfaces.uow.admin_uow import IAdminUnitOfWork
from backend.src.users.domain.interfaces.uow.user_uow import IUserUnitOfWork

admin_api_router = APIRouter(tags=["admin"])
templates_annotation = Annotated[Jinja2Templates, Depends(Provide[Container.templates])]
admin_uow_annotation = Annotated[
    IAdminUnitOfWork, Depends(Provide[Container.admin_uow])
]
user_uow_annotation = Annotated[IUserUnitOfWork, Depends(Provide[Container.user_uow])]


@admin_api_router.patch("/admin/users/{username}", response_model=UserPublic)
@inject
async def change_role(
    request: Request, uow: user_uow_annotation, username: str, is_admin: bool
) -> User:
    """Изменение роли пользователя"""
    return await ChangeRoleUseCase(uow=uow)(
        user_data=request.state.user, username=username, is_admin=is_admin
    )


@admin_api_router.post("/admin/blockings", response_model=Blocking)
@inject
async def block_user(
    request: Request,
    uow: admin_uow_annotation,
    create_data: CreateBlocking,
) -> Blocking:
    """Создание блокировки пользователя."""
    return await BlockUserUseCase(uow=uow)(
        create_data=create_data, user_data=request.state.user
    )


@admin_api_router.delete("/admin/blockings/{blocking_id}")
@inject
async def unblock_user(
    request: Request,
    uow: admin_uow_annotation,
    blocking_id: int,
) -> None:
    """Завершение блокировки пользователя."""
    await UnblockUserUseCase(uow=uow)(
        blocking_id=blocking_id, user_data=request.state.user
    )


@admin_api_router.get("/admin/users", response_model=list[UserPublic])
@inject
async def user_list(
    request: Request,
    query: Annotated[ListOfUsersParams, Query()],
    uow: admin_uow_annotation,
) -> Iterable[User]:
    """Список пользователей по заданным параметрам"""
    return await UserListUseCase(uow=uow)(
        list_conditions=query, user_data=request.state.user
    )


def _wants_json(request: Request) -> bool:
    """Отдавать json или html ответ"""
    accept = request.headers.get("accept", "")
    return "application/json" in accept


@admin_api_router.get("/admin/reports")
@inject
async def admin_reports_page(
    request: Request,
    templates: templates_annotation,
    uow: admin_uow_annotation,
    start_from: date | None = Query(None),
) -> Response:
    """Страница жалоб администратора с возможностью JSON-ответа."""
    reports = await GetReportsUseCase(uow=uow)(
        start_from=start_from, user_data=request.state.user
    )
    if _wants_json(request):
        return JSONResponse(content=[r.model_dump(mode="json") for r in reports])
    return templates.TemplateResponse(
        request=request,
        name="admin_reports.html",
        context={
            "user": request.state.user,
            "start_from": start_from.isoformat() if start_from else "",
            "reports_json": [r.model_dump(mode="json") for r in reports],
        },
    )


@admin_api_router.patch("/admin/reports/{report_id}/solve", response_model=Report)
@inject
async def solve_report(
    request: Request,
    uow: admin_uow_annotation,
    report_id: int,
) -> Report:
    """Отметить жалобу рассмотренной."""
    return await SolveReportUseCase(uow=uow)(
        report_id=report_id,
        user_data=request.state.user,
    )
