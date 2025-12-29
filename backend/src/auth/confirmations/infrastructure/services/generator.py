import secrets
import string

from backend.src.auth.confirmations.domain.interfaces.code_generator import (
    ICodeGenerator,
)


class CodeGenerator(ICodeGenerator):
    """Генератор кодов из английских букв и цифр"""

    characters = string.ascii_letters + string.digits

    def generate_account_confirm(self) -> str:
        """Код для подтверждения почты"""
        return self._code_of_length(10)

    def generate_password_confirm(self) -> str:
        """Код для подтверждения смены пароля"""
        return self._code_of_length(5)

    def _code_of_length(self, length: int) -> str:
        """Генерация кода заданной длинны"""
        return "".join(secrets.choice(self.characters) for _ in range(length))
