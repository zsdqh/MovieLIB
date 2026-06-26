import abc

from backend.src.auth.confirmations.domain.entities import EmailData


class IEmailSender(abc.ABC):
    """Класс для отправки сообщений пользователям"""

    @abc.abstractmethod
    async def send_email(self, email_data: EmailData) -> None:
        """Отправка сообщения с заданным шаблоном всем почтам в destination"""

    @abc.abstractmethod
    async def create_templates(self) -> None:
        """Создание шаблонов писем"""
