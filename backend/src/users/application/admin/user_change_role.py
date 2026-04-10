# from backend.src.auth.auth.application.check_permissions import check_admin_only
# from backend.src.auth.auth.domain.entities import TokenUser
# from backend.src.users.application.base import UserUseCase
# from backend.src.users.domain.entities import User, UserUpdate
#
#
# class ChangeRoleUseCase(UserUseCase):
#     """Изменение роли пользователя"""
#
#     async def __call__(
#         self, user_data: TokenUser, username: str, is_admin: bool
#     ) -> User:
#         check_admin_only(user_data)
#         async with self.uow:
#             obj = await self.uow.users.get_by_username(username)
#             obj = await self.uow.users.update(UserUpdate(id=obj.id,
#             is_admin=is_admin))
#         return obj
