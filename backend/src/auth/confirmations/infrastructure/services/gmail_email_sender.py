from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTP
from jinja2 import Template
from starlette.templating import Jinja2Templates

from backend.src.auth.confirmations.domain.entities import EmailData, Templates
from backend.src.auth.confirmations.domain.interfaces.email_sender import IEmailSender


class GmailEmailSender(IEmailSender):
    """Отправка почты через gmail smtp сервер"""

    def __init__(self, email: str, smtp_client: SMTP, renderer: Jinja2Templates):
        """Получение шаблонизатора и smtp-клиента как зависимостей"""
        self.client = smtp_client
        self.renderer = renderer
        self.email = email
        self.subjects: dict[Templates, str] = {}
        self.templates: dict[Templates, dict[str, Template]] = {}

    async def send_email(self, email_data: EmailData) -> None:
        async with self.client as client:
            template_name = email_data.template_name
            templates = self.templates[template_name]
            text_body = templates["text"].render(**dict(email_data.template_data))
            html_body = templates["html"].render(**dict(email_data.template_data))
            message = self._create_message(
                to_emails=email_data.destination,
                subject=self.subjects.get(template_name, "Без темы"),
                text_body=text_body,
                html_body=html_body,
            )
            await client.send_message(message)

    async def create_templates(self) -> None:
        self.templates[Templates.EMAIL_CONFIRMATION] = {
            "text": self.renderer.get_template("email/email_confirmation.txt"),
            "html": self.renderer.get_template("email/email_confirmation.html"),
        }
        self.subjects[Templates.EMAIL_CONFIRMATION] = "Подтверждение почты"
        self.templates[Templates.PASSWORD_CONFIRMATION] = {
            "text": self.renderer.get_template("email/password_confirmation.txt"),
            "html": self.renderer.get_template("email/password_confirmation.html"),
        }
        self.subjects[Templates.PASSWORD_CONFIRMATION] = "Подтверждение пароля"

    def _create_message(
        self, to_emails: list[str], subject: str, text_body: str, html_body: str
    ) -> MIMEMultipart:
        """Создание сообщения, готового для отправки"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.email
        message["To"] = ", ".join(to_emails)

        text_part = MIMEText(text_body, "plain", "utf-8")
        message.attach(text_part)

        html_part = MIMEText(html_body, "html", "utf-8")
        message.attach(html_part)

        return message
