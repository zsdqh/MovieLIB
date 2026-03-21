from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.entities import CommentPage


class GetMovieCommentsUseCase(CommentUseCase):
    """
    Получение комментариев к фильму с пагинацией и
    рекурсивной загрузкой всех комментариев
    """

    async def __call__(self, movie_id: int, page: int) -> CommentPage:
        async with self.uow:
            return await self.uow.comments.get_movie_comments(movie_id, page)
