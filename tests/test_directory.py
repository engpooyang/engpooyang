"""Tests for staff directory lookup."""

from unittest.mock import patch

from src.models.schemas import (
    BusinessHours,
    CompanyConfig,
    DirectoryConfig,
    EmergencyContact,
    StaffMember,
)
from src.services.directory import lookup_staff


def _mock_directory():
    return DirectoryConfig(
        staff=[
            StaffMember(
                name="John Tan",
                role="Sales Manager",
                department="Sales",
                phone="+6591234567",
                email="john@test.com",
            ),
            StaffMember(
                name="Jane Lim",
                role="Technical Support Lead",
                department="Support",
                phone="+6598765432",
                email="jane@test.com",
            ),
        ]
    )


def _mock_company():
    return CompanyConfig(
        company_name="Test Co",
        greeting="Hello",
        business_hours=BusinessHours(
            timezone="Asia/Singapore",
            weekdays="00:00-23:59",  # Always open for testing
            saturday="00:00-23:59",
            sunday="00:00-23:59",
        ),
        after_hours_message="Closed",
        emergency_contact=EmergencyContact(name="Boss", phone="+6590000000"),
    )


@patch("src.services.directory.get_company_config", return_value=_mock_company())
@patch("src.services.directory.get_directory_config", return_value=_mock_directory())
def test_lookup_by_department(mock_dir, mock_company):
    result = lookup_staff("Sales")
    assert result.found is True
    assert result.name == "John Tan"
    assert result.department == "Sales"


@patch("src.services.directory.get_company_config", return_value=_mock_company())
@patch("src.services.directory.get_directory_config", return_value=_mock_directory())
def test_lookup_by_name(mock_dir, mock_company):
    result = lookup_staff("Jane")
    assert result.found is True
    assert result.name == "Jane Lim"


@patch("src.services.directory.get_company_config", return_value=_mock_company())
@patch("src.services.directory.get_directory_config", return_value=_mock_directory())
def test_lookup_not_found(mock_dir, mock_company):
    result = lookup_staff("Marketing")
    assert result.found is False


@patch("src.services.directory.get_company_config", return_value=_mock_company())
@patch("src.services.directory.get_directory_config", return_value=_mock_directory())
def test_lookup_by_role(mock_dir, mock_company):
    result = lookup_staff("Technical Support")
    assert result.found is True
    assert result.name == "Jane Lim"
