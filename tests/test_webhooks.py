"""Tests for webhook endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app
from src.models.schemas import (
    DirectoryConfig,
    RepeatCallerConfig,
    SpamRulesConfig,
    StaffMember,
)

client = TestClient(app)


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


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ai-landline-agent"


@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
@patch("src.services.caller_lookup.get_directory_config", return_value=_mock_directory())
def test_check_caller_blocked(mock_dir, mock_spam):
    response = client.post(
        "/tools/check-caller",
        json={"caller_number": "+6561111111"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["blocked"] is True


@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
@patch("src.services.caller_lookup.get_directory_config", return_value=_mock_directory())
def test_check_caller_known(mock_dir, mock_spam):
    response = client.post(
        "/tools/check-caller",
        json={"caller_number": "+6591234567"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["known_contact"] == "John Tan"


@patch("src.services.call_log.get_spam_rules_config", return_value=_mock_spam_config())
def test_report_spam(mock_spam):
    response = client.post(
        "/tools/report-spam",
        json={"caller_number": "+6599887766", "reason": "sales call"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["logged"] is True


def test_transfer_call():
    response = client.post(
        "/tools/transfer-call",
        json={"destination_number": "+6591234567"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_transfer_call_no_number():
    response = client.post(
        "/tools/transfer-call",
        json={"destination_number": ""},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
