import abc

from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class UserUseCase(abc.ABC):
    """Класс, реализующий одно действие с пользователем"""

    def __init__(self, uow: IUserUnitOfWork):
        """Присвоение зависимостей извне для действия"""
        self.uow = uow
