from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.confirmations.application.send_email import (
    SendEmailWithTokenUseCase,
)
from backend.src.auth.confirmations.domain.entities import (
    ConfCreate,
    Confirmation,
    Templates,
)
from backend.src.auth.confirmations.domain.interfaces.code_generator import (
    ICodeGenerator,
)
from backend.src.auth.confirmations.domain.interfaces.conf_repo import IConfRepository
from backend.src.auth.confirmations.domain.interfaces.conf_uow import IConfUnitOfWork
from backend.src.auth.confirmations.domain.interfaces.email_sender import IEmailSender


class SendPasswordConfirmationUseCase(SendEmailWithTokenUseCase):
    """Отправка подтверждения для изменения пароля"""

    def __init__(
        self,
        cache_repository: IConfRepository,
        uow: IConfUnitOfWork,
        generator: ICodeGenerator,
        sender: IEmailSender,
    ):
        self.cache_repository = cache_repository
        super().__init__(uow=uow, generator=generator, sender=sender)

    async def __call__(self, user_data: TokenUser) -> Confirmation:
        """Отправка кода подтверждения и сохранение его в кеш"""
        token = self.generator.generate_password_confirm()

        await self._send_email(user_data, token, Templates.PASSWORD_CONFIRMATION)

        conf_create_data = ConfCreate(user_id=user_data.sub, token=token)

        # В отличие от хранения в БД, в кеше не нужно обновлять данные
        # в случае их наличия, можно просто перезаписать значение
        obj = await self.cache_repository.create(conf_create_data)

        return obj
