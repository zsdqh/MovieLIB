import uuid

from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.entities import CommentPage


class GetUserCommentsUseCase(CommentUseCase):
    """Получение комментариев пользователя с пагинацией, без ответов"""

    async def __call__(self, user_id: uuid.UUID, page: int) -> CommentPage:
        async with self.uow:
            return await self.uow.comments.get_user_comments(user_id, page)
