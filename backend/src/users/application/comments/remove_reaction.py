from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.entities import Comment, RemoveReaction


class RemoveReactionUseCase(CommentUseCase):
    """Удаление реакции на комментарий"""

    async def __call__(self, comment_id: int, user_data: TokenUser) -> Comment:
        async with self.uow:
            reaction_data = RemoveReaction(comment_id=comment_id, user_id=user_data.sub)
            return await self.uow.comments.remove_reaction(reaction_data)
