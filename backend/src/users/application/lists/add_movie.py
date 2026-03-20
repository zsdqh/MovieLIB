from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.lists.base import ListUseCase
from backend.src.users.domain.entities import ListMovie, UserList


class AddMovieUseCase(ListUseCase):
    """Добавление фильма в пользовательский список"""

    async def __call__(
        self, list_id: int, movie_id: int, user_data: TokenUser
    ) -> UserList:
        async with self.uow:
            to_add = ListMovie(
                list_id=list_id, movie_id=movie_id, user_id=user_data.sub
            )
            res = await self.uow.lists.add_movie(to_add)
        return res
