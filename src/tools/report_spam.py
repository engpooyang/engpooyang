"""ElevenLabs custom tool: Report a caller as spam and auto-block repeat offenders."""

from src.models.schemas import ReportSpamRequest, ReportSpamResponse
from src.services.call_log import record_spam_call


def handle_report_spam(request: ReportSpamRequest) -> ReportSpamResponse:
    was_blocked = record_spam_call(request.caller_number)

    if was_blocked:
        return ReportSpamResponse(
            logged=True,
            blocked=True,
            message=f"Number {request.caller_number} has been logged and auto-blocked due to repeated spam calls.",
        )

    return ReportSpamResponse(
        logged=True,
        blocked=False,
        message=f"Number {request.caller_number} has been logged as spam.",
    )
