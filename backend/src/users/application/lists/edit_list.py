from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.lists.base import ListUseCase
from backend.src.users.domain.dtos import EditListDTO
from backend.src.users.domain.entities import EditList, UserList


class EditListUseCase(ListUseCase):
    """Изменение данных о пользовательском списке"""

    async def __call__(
        self, list_id: int, user_data: TokenUser, edit_data: EditListDTO
    ) -> UserList:
        async with self.uow:
            to_edit = EditList(
                **edit_data.model_dump(), id=list_id, user_id=user_data.sub
            )
            return await self.uow.lists.edit_list(to_edit)
