from backend.src.users.domain.interfaces.uow.comment_uow import ICommentUnitOfWork


class CommentUseCase:
    """Вариант использования для работы с комментариями"""

    def __init__(self, comment_uow: ICommentUnitOfWork):
        """Получение зависимости единицы работы с комментариями"""
        self.uow = comment_uow
