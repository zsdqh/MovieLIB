import abc
import uuid

from backend.src.users.domain.entities import (
    Comment,
    CommentPage,
    CommentReaction,
    CreateComment,
    DeleteComment,
    RemoveReaction,
)


class ICommentRepository(abc.ABC):
    """Репозиторий для работы с комменатриями"""

    @abc.abstractmethod
    async def create_comment(self, comment_data: CreateComment) -> Comment:
        """Создание комментария"""

    @abc.abstractmethod
    async def delete_comment(
        self, delete_data: DeleteComment, is_admin: bool = False
    ) -> None:
        """Рекурсивное удаление комментария вместе с ответами"""

    @abc.abstractmethod
    async def add_reaction(self, reaction_data: CommentReaction) -> Comment:
        """Добавление реакции на комментарий"""

    @abc.abstractmethod
    async def remove_reaction(self, reaction_data: RemoveReaction) -> Comment:
        """Удаление реакции на комментарий"""

    @abc.abstractmethod
    async def get_user_comments(self, user_id: uuid.UUID, page: int = 0) -> CommentPage:
        """Получение всех комментариев пользователя с пагинацией"""

    @abc.abstractmethod
    async def get_movie_comments(self, movie_id: int, page: int = 0) -> CommentPage:
        """Получение всех комментариев к фильму"""
