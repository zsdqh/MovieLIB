from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.lists.base import ListUseCase
from backend.src.users.domain.entities import ListMovie, UserList


class RemoveMovieUseCase(ListUseCase):
    """Удаление фильма из пользовательского списка"""

    async def __call__(
        self, list_id: int, movie_id: int, user_data: TokenUser
    ) -> UserList:
        async with self.uow:
            to_remove = ListMovie(
                list_id=list_id, movie_id=movie_id, user_id=user_data.sub
            )
            res = await self.uow.lists.remove_movie(to_remove)
        return res
