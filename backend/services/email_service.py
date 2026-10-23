"""
services/email_service.py — Async SMTP email sender
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
from ..config import settings


def _send_sync(to: str, subject: str, body_html: str) -> None:
    """Blocking SMTP send — run inside a thread pool."""
    if not settings.SMTP_USER:
        print(f"[email_service] SMTP not configured — skipping email to {to}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.EMAIL_FROM or settings.SMTP_USER
    msg["To"]      = to
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(msg["From"], [to], msg.as_string())


async def send_email(to: str, subject: str, body_html: str) -> None:
    """Async wrapper — runs blocking SMTP in the default executor."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_sync, to, subject, body_html)


async def send_followup(customer_name: str, customer_email: str, message: str) -> None:
    """Send a follow-up email to a customer."""
    html = f"""
    <div dir="rtl" style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <h2>مرحباً {customer_name}</h2>
      <p>{message}</p>
      <hr/>
      <p style="color:#888;font-size:12px">للإلغاء الاشتراك، رد بكلمة "إيقاف"</p>
    </div>"""
    await send_email(customer_email, "متابعة من فريقنا", html)
