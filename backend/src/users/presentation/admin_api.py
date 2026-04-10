# from typing import Annotated, Iterable
#
# from dependency_injector.wiring import inject
# from fastapi import APIRouter
# from fastapi.params import Query
# from starlette.requests import Request
#
# from backend.src.users.application.admin.user_block import UserBlockUseCase
# from backend.src.users.application.admin.user_change_role import ChangeRoleUseCase
# from backend.src.users.application.admin.user_list import UserListUseCase
# from backend.src.users.domain.dtos import ListOfUsersParams
# from backend.src.users.domain.entities import User, UserPublic
# from backend.src.users.presentation.users_api import user_uow_annotation
#
# admin_api_router = APIRouter(tags=["admin"])
#
#
# @admin_api_router.patch("/users/{username}", response_model=UserPublic)
# @inject
# async def change_role(
#     request: Request, uow: user_uow_annotation, username: str, is_admin: bool
# ) -> User:
#     """Изменение роли пользователя"""
#     return await ChangeRoleUseCase(uow=uow)(
#         user_data=request.state.user, username=username, is_admin=is_admin
#     )
#
#
# @admin_api_router.get("/block/{username}", response_model=UserPublic)
# @inject
# async def block(username: str, uow: user_uow_annotation, request: Request) -> User:
#     """Блокировка пользователя"""
#     return await UserBlockUseCase(uow=uow)(
#         username=username, new_status=True, user_data=request.state.user
#     )
#
#
# @admin_api_router.get("/unblock/{username}", response_model=UserPublic)
# @inject
# async def unblock(username: str, uow: user_uow_annotation, request: Request) -> User:
#     """Разблокировка пользователя"""
#     return await UserBlockUseCase(uow=uow)(
#         username=username, new_status=False, user_data=request.state.user
#     )
#
#
# @admin_api_router.get("/users", response_model=list[UserPublic])
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
