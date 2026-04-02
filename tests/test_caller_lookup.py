"""Tests for caller lookup and spam detection."""

from unittest.mock import patch

from src.models.schemas import (
    DirectoryConfig,
    RepeatCallerConfig,
    SpamRulesConfig,
    StaffMember,
)
from src.services.caller_lookup import check_caller


def _mock_spam_config():
    return SpamRulesConfig(
        blocked_numbers=["+6561111111"],
        spam_categories={},
        repeat_caller=RepeatCallerConfig(),
        decline_message="Not interested.",
    )


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
        ]
    )


@patch("src.services.caller_lookup.get_directory_config", return_value=_mock_directory())
@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
def test_blocked_number_is_rejected(mock_spam, mock_dir):
    result = check_caller("+6561111111")
    assert result.blocked is True
    assert result.action == "hang_up"


@patch("src.services.caller_lookup.get_directory_config", return_value=_mock_directory())
@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
def test_known_contact_is_allowed(mock_spam, mock_dir):
    result = check_caller("+6591234567")
    assert result.known_contact == "John Tan"
    assert result.action == "allow"


@patch("src.services.caller_lookup.get_directory_config", return_value=_mock_directory())
@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
def test_unknown_caller_is_allowed(mock_spam, mock_dir):
    result = check_caller("+6599999999")
    assert result.blocked is False
    assert result.action == "allow"
