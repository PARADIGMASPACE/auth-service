import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.responses import JSONResponse
from auth_service.core.redis_client import RedisClient

load_dotenv()
from auth_service.core.utils import generate_token_for_email

MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM = os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"), os.getenv("MAIL_FROM")
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

redis_client = RedisClient()


async def generate_link(email):
    token = generate_token_for_email()
    confirmation_url = f"http://localhost:8001/email/confirm-email?token={token}&email={email}"
    return confirmation_url, token



async def generate_reset_link(email: str):
    token = generate_token_for_email()
    reset_url = f"http://localhost:8001/change/reset-password?token={token}&email={email}"
    await redis_client.set_token(email, token, expire=3600)
    return reset_url


async def send_resset_password_email(email: str, new_password: str):
    with open('/auth_service/mail/templates/password_reset.html') as file:
        html_content = file.read().replace('{{ new_password }}', new_password)

    message = MessageSchema(
        subject="Reset Password",
        recipients=[email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "Email has been sent"})


async def send_confirmation_email(email: str):
    confirmation_url, token = await generate_link(email)
    with open('/auth_service/mail/templates/registration_confirmation.html') as file:
        html_content = file.read().replace('{{ confirmation_url }}', confirmation_url)

    message = MessageSchema(
        subject="Email Confirmation",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    print(confirmation_url)
    await redis_client.set_token(email, token, expire=7200)
    await redis_client.close()
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "Email has been sent"})