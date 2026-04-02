"""Webhook endpoints for ElevenLabs custom tools and Twilio status callbacks."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException

from src.models.schemas import (
    CheckCallerRequest,
    LookupStaffRequest,
    ReportSpamRequest,
    Settings,
    TakeMessageRequest,
    TransferCallRequest,
)
from src.tools.check_caller import handle_check_caller
from src.tools.lookup_staff import handle_lookup_staff
from src.tools.report_spam import handle_report_spam
from src.tools.take_message import handle_take_message
from src.tools.transfer_call import handle_transfer_call

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])

_settings: Settings | None = None


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def _verify_auth(authorization: str | None) -> None:
    """Verify the API secret key from the Authorization header."""
    settings = _get_settings()
    if not settings.api_secret_key:
        return  # No auth configured — allow all (dev mode)
    expected = f"Bearer {settings.api_secret_key}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/check-caller")
def check_caller(
    request: CheckCallerRequest,
    authorization: str | None = Header(default=None),
):
    """ElevenLabs calls this to check if a caller is blocked or a repeat offender."""
    _verify_auth(authorization)
    result = handle_check_caller(request)
    return result.model_dump()


@router.post("/report-spam")
def report_spam(
    request: ReportSpamRequest,
    authorization: str | None = Header(default=None),
):
    """ElevenLabs calls this to log a spam caller and potentially auto-block."""
    _verify_auth(authorization)
    result = handle_report_spam(request)
    return result.model_dump()


@router.post("/lookup-staff")
def lookup_staff(
    request: LookupStaffRequest,
    authorization: str | None = Header(default=None),
):
    """ElevenLabs calls this to find a staff member by name or department."""
    _verify_auth(authorization)
    result = handle_lookup_staff(request)
    return result.model_dump()


@router.post("/transfer-call")
def transfer_call(
    request: TransferCallRequest,
    authorization: str | None = Header(default=None),
):
    """ElevenLabs calls this to get transfer destination details."""
    _verify_auth(authorization)
    result = handle_transfer_call(request)
    return result.model_dump()


@router.post("/take-message")
async def take_message(
    request: TakeMessageRequest,
    authorization: str | None = Header(default=None),
):
    """ElevenLabs calls this to record a message and send notifications."""
    _verify_auth(authorization)
    result = await handle_take_message(request)
    return result.model_dump()


# --- Twilio status callback ---

twilio_router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@twilio_router.post("/call-status")
async def call_status(request: dict | None = None):
    """Twilio call status callback for logging purposes."""
    logger.info("Twilio call status: %s", request)
    return {"status": "received"}
