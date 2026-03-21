from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.comments.base import CommentUseCase
from backend.src.users.domain.dtos import CreateCommentDTO
from backend.src.users.domain.entities import Comment, CreateComment


class AddCommentUseCase(CommentUseCase):
    """Добавление комментария"""

    async def __call__(
        self, create_data: CreateCommentDTO, movie_id: int, user_data: TokenUser
    ) -> Comment:
        async with self.uow:
            has_answer_to = (
                create_data.answer_to is not None and create_data.answer_to != -1
            )
            to_create = CreateComment(
                **create_data.model_dump(
                    exclude={} if has_answer_to else {"answer_to"}
                ),
                user_id=user_data.sub,
                movie_id=movie_id if not has_answer_to else None
            )
            return await self.uow.comments.create_comment(to_create)
