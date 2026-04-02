"""Staff directory lookup and business hours service."""

from __future__ import annotations

from datetime import datetime

import pytz

from src.models.schemas import LookupStaffResponse, StaffMember
from src.services.config_loader import get_company_config, get_directory_config


def _is_business_hours() -> bool:
    """Check if the current time is within business hours."""
    config = get_company_config()
    tz = pytz.timezone(config.business_hours.timezone)
    now = datetime.now(tz)
    day = now.strftime("%A").lower()

    if day == "sunday":
        hours_str = config.business_hours.sunday
    elif day == "saturday":
        hours_str = config.business_hours.saturday
    else:
        hours_str = config.business_hours.weekdays

    if hours_str is None:
        return False

    start_str, end_str = hours_str.split("-")
    start_h, start_m = map(int, start_str.split(":"))
    end_h, end_m = map(int, end_str.split(":"))

    current_minutes = now.hour * 60 + now.minute
    start_minutes = start_h * 60 + start_m
    end_minutes = end_h * 60 + end_m

    return start_minutes <= current_minutes <= end_minutes


def _match_staff(query: str) -> StaffMember | None:
    """Find a staff member by name or department (fuzzy match)."""
    directory = get_directory_config()
    query_lower = query.lower()

    # Exact department match
    for staff in directory.staff:
        if staff.department.lower() == query_lower:
            return staff

    # Partial name match
    for staff in directory.staff:
        if query_lower in staff.name.lower():
            return staff

    # Partial role match
    for staff in directory.staff:
        if query_lower in staff.role.lower():
            return staff

    # Partial department match
    for staff in directory.staff:
        if query_lower in staff.department.lower():
            return staff

    return None


def lookup_staff(query: str) -> LookupStaffResponse:
    """Look up a staff member and check availability."""
    staff = _match_staff(query)

    if staff is None:
        return LookupStaffResponse(
            found=False,
            message=f"No staff member found matching '{query}'.",
        )

    available = _is_business_hours()

    if not available:
        config = get_company_config()
        return LookupStaffResponse(
            found=True,
            name=staff.name,
            role=staff.role,
            department=staff.department,
            phone=staff.phone,
            available=False,
            message=config.after_hours_message,
        )

    return LookupStaffResponse(
        found=True,
        name=staff.name,
        role=staff.role,
        department=staff.department,
        phone=staff.phone,
        available=True,
        message=f"{staff.name} ({staff.role}) is available.",
    )
