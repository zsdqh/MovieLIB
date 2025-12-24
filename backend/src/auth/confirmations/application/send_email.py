import abc

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.confirmations.domain.entities import (
    EmailData,
    TemplateData,
    Templates,
)
from backend.src.auth.confirmations.domain.interfaces.code_generator import (
    ICodeGenerator,
)
from backend.src.auth.confirmations.domain.interfaces.conf_uow import IConfUnitOfWork
from backend.src.auth.confirmations.domain.interfaces.email_sender import IEmailSender


class SendEmailWithTokenUseCase(abc.ABC):
    """
    Абстрактный юз кейс, реализующий отправку сообщения с кодом подтверждения на почту
    """

    def __init__(
        self, uow: IConfUnitOfWork, sender: IEmailSender, generator: ICodeGenerator
    ) -> None:
        """Зависимости для создания и отправки подтверждения"""
        self.uow = uow
        self.sender = sender
        self.generator = generator

    async def _send_email(
        self, user_data: TokenUser, token: str, template_name: Templates
    ) -> None:
        """Отправка подтверждения с кодом подтверждения"""
        email_data = EmailData(
            destination=[str(user_data.email)],
            template_name=template_name,
            template_data=TemplateData(token=token, username=user_data.username),
        )

        await self.sender.send_email(email_data)
