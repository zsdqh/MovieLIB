from backend.src.users.domain.interfaces.uow.rating_uow import IRatingUnitOfWork


class RatingUseCase:
    """Вариант использования для работы с рейтингами фильмов"""

    def __init__(self, rating_uow: IRatingUnitOfWork):
        """Получение зависимости единицы работы с рейтингами"""
        self.uow = rating_uow
