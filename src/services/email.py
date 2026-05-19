from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.settings import settings


def _is_mail_configured() -> bool:
    required = [
        settings.MAIL_USERNAME,
        settings.MAIL_PASSWORD,
        settings.MAIL_FROM,
        settings.MAIL_PORT,
        settings.MAIL_SERVER,
    ]
    return all(required)


def _mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
    )


async def send_verification_email(*, email: EmailStr, username: str, base_url: str) -> None:
    if not _is_mail_configured():
        return

    token = create_email_token(email=str(email))
    message = MessageSchema(
        subject="Confirm your email",
        recipients=[str(email)],
        template_body={"username": username, "host": base_url, "token": token},
        subtype=MessageType.html,
    )

    fm = FastMail(_mail_config())
    await fm.send_message(message, template_name="verify_email.html")

