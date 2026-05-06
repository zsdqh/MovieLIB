from backend.src.users.domain.interfaces.uow.admin_uow import IAdminUnitOfWork


class AdminUseCase:
    """Базовый класс варианта использования для действий администратора"""

    def __init__(self, uow: IAdminUnitOfWork):
        """Присвоение зависимостей извне для варианта использования"""
        self.uow = uow
