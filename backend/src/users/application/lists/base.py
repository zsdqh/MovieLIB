from backend.src.users.domain.interfaces.uow.list_uow import IListUnitOfWork


class ListUseCase:
    """Вариант использования для работы с пользовательскими списками фильмов"""

    def __init__(self, list_uow: IListUnitOfWork):
        """Получение зависимости единицы работы со списками"""
        self.uow = list_uow
