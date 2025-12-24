import abc


class ICodeGenerator(abc.ABC):
    """Генератор кодов для подтверждений действий"""

    @abc.abstractmethod
    def generate_account_confirm(self) -> str:
        """Код для подтверждения почты"""

    @abc.abstractmethod
    def generate_password_confirm(self) -> str:
        """Код для сброса пароля"""
