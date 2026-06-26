import aioboto3.session

from backend.src.auth.confirmations.domain.entities import EmailData, Templates
from backend.src.auth.confirmations.domain.interfaces.email_sender import IEmailSender
from backend.src.core.config import AWSSettings


class SESCustomClient(IEmailSender):
    """Клиент для отправки сообщений через AWS SES"""

    def __init__(self, source: str, settings: AWSSettings):
        """
        Создание AWS сессии
        :param source: почта, от чьего имени отправляются сообщения
        """
        self.session = aioboto3.session.Session(
            region_name="us-east-1",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self.source = source
        self.settings = settings

    async def send_email(self, email_data: EmailData) -> None:
        """Отправка сообщения с заданным шаблоном заданным пользователям"""
        async with self.session.client(
            "ses", endpoint_url=self.settings.aws_url
        ) as client:
            await client.send_templated_email(
                Source=self.source,
                Destination={"ToAddresses": list(email_data.destination)},
                Template=email_data.template_name,
                TemplateData=email_data.template_data.model_dump_json(),
            )

    async def create_templates(self) -> None:
        """Добавление шаблонов подтверждения"""
        async with self.session.client(
            "ses", endpoint_url=self.settings.aws_url
        ) as client:
            try:
                await client.create_template(
                    Template={
                        "TemplateName": Templates.EMAIL_CONFIRMATION,
                        "SubjectPart": "Confirm your email",
                        "TextPart": "{{username}}, use this code to "
                        "confirm your email: {{token}}",
                        "HtmlPart": "<p>Use this code to confirm your email: "
                        "<strong>{{token}}</strong></p>",
                    }
                )
                await client.create_template(
                    Template={
                        "TemplateName": Templates.PASSWORD_CONFIRMATION,
                        "SubjectPart": "Reset your password",
                        "TextPart": "<b>{{username}}</b>, "
                        "use this code to reset your password: {{token}}",
                        "HtmlPart": "<p>Use this code to reset your password: "
                        "<strong>{{token}}</strong></p>",
                    }
                )
            except client.exceptions.AlreadyExistsException:
                pass
