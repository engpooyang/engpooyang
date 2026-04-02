"""Notification dispatch service for messages taken by the AI agent."""

from __future__ import annotations

import logging

import httpx

from src.models.schemas import Settings, TakeMessageRequest

logger = logging.getLogger(__name__)

_settings: Settings | None = None


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


async def send_notification(message: TakeMessageRequest) -> bool:
    """Send a message notification via all configured channels."""
    settings = _get_settings()
    success = False

    text = (
        f"New message for {message.intended_recipient or 'General'}:\n"
        f"From: {message.caller_name}"
        f"{' (' + message.caller_company + ')' if message.caller_company else ''}\n"
        f"Phone: {message.caller_phone}\n"
        f"Message: {message.message}"
    )

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
                        "message": message.message,
                        "intended_recipient": message.intended_recipient,
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
