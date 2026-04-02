"""ElevenLabs custom tool: Check caller against blocked list and repeat offender log."""

from src.models.schemas import CheckCallerRequest, CheckCallerResponse
from src.services.caller_lookup import check_caller


def handle_check_caller(request: CheckCallerRequest) -> CheckCallerResponse:
    return check_caller(request.caller_number)
