"""ElevenLabs custom tool: Look up a staff member by name or department."""

from src.models.schemas import LookupStaffRequest, LookupStaffResponse
from src.services.directory import lookup_staff


def handle_lookup_staff(request: LookupStaffRequest) -> LookupStaffResponse:
    return lookup_staff(request.query)
