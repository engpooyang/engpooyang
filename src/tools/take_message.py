"""ElevenLabs custom tool: Record a message and dispatch notifications."""

import logging

import asyncio

from src.models.schemas import TakeMessageRequest, TakeMessageResponse
from src.services.notifications import send_notification

logger = logging.getLogger(__name__)


async def handle_take_message(request: TakeMessageRequest) -> TakeMessageResponse:
    """Store the message and fire notification webhooks."""
    logger.info(
        "Message from %s (%s): %s — for %s",
        request.caller_name,
        request.caller_phone,
        request.message,
        request.intended_recipient or "General",
    )

    notified = await send_notification(request)

    return TakeMessageResponse(
        success=True,
        message=(
            "Your message has been recorded and the team has been notified."
            if notified
            else "Your message has been recorded. We will get back to you."
        ),
    )
