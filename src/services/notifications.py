"""Notification dispatch service for messages taken by the AI agent."""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

import httpx

from src.models.schemas import Settings, TakeMessageRequest

logger = logging.getLogger(__name__)

_settings: Settings | None = None


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


async def send_email_to_staff(staff_email: str, message: TakeMessageRequest) -> bool:
    """Send a callback request email directly to a staff member."""
    settings = _get_settings()

    if not settings.notification_email_smtp_host or not settings.notification_email_from:
        logger.warning("SMTP not configured — cannot send staff email")
        return False

    subject = f"Callback Request from {message.caller_name}"
    body = (
        f"Hi,\n\n"
        f"You received a call while you were unavailable. Please call back at your earliest convenience.\n\n"
        f"--- Caller Details ---\n"
        f"Name: {message.caller_name}\n"
        f"Company: {message.caller_company or 'N/A'}\n"
        f"Phone: {message.caller_phone}\n"
        f"Email: {message.caller_email or 'N/A'}\n\n"
        f"--- Message ---\n"
        f"{message.message}\n\n"
        f"---\n"
        f"This message was recorded by Ava, Appvantage's AI phone assistant."
    )

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.notification_email_from
        msg["To"] = staff_email

        with smtplib.SMTP(settings.notification_email_smtp_host, settings.notification_email_smtp_port) as server:
            server.starttls()
            server.login(settings.notification_email_from, settings.notification_email_password)
            server.send_message(msg)

        logger.info("Callback email sent to %s", staff_email)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", staff_email)
        return False


async def send_notification(message: TakeMessageRequest, staff_email: str = "") -> bool:
    """Send a message notification via all configured channels.

    If staff_email is provided, also sends a direct callback email to that staff member.
    """
    settings = _get_settings()
    success = False

    text = (
        f"Callback request for {message.intended_recipient or 'General'}:\n"
        f"From: {message.caller_name}"
        f"{' (' + message.caller_company + ')' if message.caller_company else ''}\n"
        f"Phone: {message.caller_phone}\n"
        f"Email: {message.caller_email or 'N/A'}\n"
        f"Message: {message.message}"
    )

    # Send direct email to the staff member
    if staff_email:
        email_sent = await send_email_to_staff(staff_email, message)
        if email_sent:
            success = True

    # Slack webhook
    if settings.slack_webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.slack_webhook_url,
                    json={"text": text},
                    timeout=10,
                )
                if resp.status_code == 200:
                    success = True
                    logger.info("Slack notification sent")
        except Exception:
            logger.exception("Failed to send Slack notification")

    # Generic webhook
    if settings.notification_webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    settings.notification_webhook_url,
                    json={
                        "caller_name": message.caller_name,
                        "caller_company": message.caller_company,
                        "caller_phone": message.caller_phone,
                        "caller_email": message.caller_email,
                        "message": message.message,
                        "intended_recipient": message.intended_recipient,
                        "staff_email": staff_email,
                    },
                    timeout=10,
                )
                if resp.is_success:
                    success = True
                    logger.info("Webhook notification sent")
        except Exception:
            logger.exception("Failed to send webhook notification")

    if not success:
        logger.warning("No notification channel succeeded — message logged only")
        logger.info("Message record: %s", text)

    return success
