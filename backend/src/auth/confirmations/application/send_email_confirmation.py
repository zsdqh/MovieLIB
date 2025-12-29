from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.confirmations.application.send_email import (
    SendEmailWithTokenUseCase,
)
from backend.src.auth.confirmations.domain.entities import (
    ConfCreate,
    Confirmation,
    ConfUpdate,
    Templates,
)
from backend.src.core.domain.exceptions import AlreadyExistsException


class SendEmailConfirmationUseCase(SendEmailWithTokenUseCase):
    """Отправка кода подтверждения почты аккаунта"""

    async def __call__(self, user_data: TokenUser) -> Confirmation:
        """
        Создание токена и его отправка пользователю
        если это повторный запрос на отправку кода, то код
        перезаписывается вместо создания нового объекта подтверждения
        """
        token = self.generator.generate_account_confirm()

        await self._send_email(user_data, token, Templates.EMAIL_CONFIRMATION)

        async with self.uow:
            try:
                # Создаем подтверждение, если это первая попытка
                obj = await self.uow.confirmations.create(
                    ConfCreate(user_id=user_data.sub, token=token)
                )
            except AlreadyExistsException:
                # Изменяем подтверждение при повторном вызове
                await self.uow.rollback()
                obj = await self.uow.confirmations.update(
                    conf_new_data=ConfUpdate(user_id=user_data.sub, token=token)
                )

        return obj
