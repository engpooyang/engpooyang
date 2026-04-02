"""Caller identification and spam checking service."""

from __future__ import annotations

from src.models.schemas import CheckCallerResponse
from src.services.call_log import is_blocked, is_repeat_offender
from src.services.config_loader import get_directory_config


def check_caller(caller_number: str) -> CheckCallerResponse:
    """Check a caller number against blocked list, repeat offenders, and known contacts."""

    # Check if blocked
    if is_blocked(caller_number):
        return CheckCallerResponse(
            blocked=True,
            action="hang_up",
        )

    # Check if repeat offender
    if is_repeat_offender(caller_number):
        return CheckCallerResponse(
            is_repeat_offender=True,
            action="decline",
        )

    # Check if known contact
    directory = get_directory_config()
    for staff in directory.staff:
        if staff.phone == caller_number:
            return CheckCallerResponse(
                known_contact=staff.name,
                action="allow",
            )

    # Unknown caller — allow but let the agent decide based on conversation
    return CheckCallerResponse(action="allow")
