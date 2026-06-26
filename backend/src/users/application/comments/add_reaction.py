from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.entities import Comment, CommentReaction


class AddReactionUseCase(CommentUseCase):
    """Добавление реакции на комментарий"""

    async def __call__(
        self, comment_id: int, user_data: TokenUser, reaction: bool
    ) -> Comment:
        async with self.uow:
            reaction_data = CommentReaction(
                comment_id=comment_id, user_id=user_data.sub, reaction=reaction
            )
            return await self.uow.comments.add_reaction(reaction_data)
