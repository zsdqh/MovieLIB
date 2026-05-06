from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.entities import DeleteComment


class DeleteCommentUseCase(CommentUseCase):
    """Удаление комментария"""

    async def __call__(self, comment_id: int, user_data: TokenUser) -> None:
        async with self.uow:
            return await self.uow.comments.delete_comment(
                DeleteComment(comment_id=comment_id, user_id=user_data.sub),
                is_admin=user_data.is_admin,
            )
