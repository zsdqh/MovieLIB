from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.lists.base import ListUseCase
from backend.src.users.domain.entities import DeleteList


class DeleteListUseCase(ListUseCase):
    """Удаление пользовательского списка"""

    async def __call__(self, list_id: int, user_data: TokenUser) -> None:
        async with self.uow:
            await self.uow.lists.delete_list(
                DeleteList(list_id=list_id, user_id=user_data.sub)
            )
