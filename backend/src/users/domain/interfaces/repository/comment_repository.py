import abc

from backend.src.users.domain.entities import (
    Comment,
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
    async def delete_comment(self, delete_data: DeleteComment) -> None:
        """Рекурсивное удаление комментария вместе с ответами"""

    @abc.abstractmethod
    async def add_reaction(self, reaction_data: CommentReaction) -> Comment:
        """Добавление реакции на комментарий"""

    @abc.abstractmethod
    async def remove_reaction(self, reaction_data: RemoveReaction) -> Comment:
        """Удаление реакции на комментарий"""
