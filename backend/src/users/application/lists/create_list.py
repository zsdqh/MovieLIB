from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.lists.base import ListUseCase
from backend.src.users.domain.dtos import CreateListDTO
from backend.src.users.domain.entities import CreateList, UserList


class CreateListUseCase(ListUseCase):
    """Создание пользовательского списка"""

    async def __call__(
        self, create_data: CreateListDTO, user_data: TokenUser
    ) -> UserList:
        async with self.uow:
            to_create = CreateList(user_id=user_data.sub, **create_data.model_dump())
            res = await self.uow.lists.create_list(to_create)
        return res
