"""Pydantic models for configuration, API requests, and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# --- App Settings ---


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    elevenlabs_api_key: str = ""
    elevenlabs_agent_id: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    backend_url: str = "http://localhost:8000"
    api_secret_key: str = ""
    slack_webhook_url: str = ""
    notification_email_smtp_host: str = ""
    notification_email_smtp_port: int = 587
    notification_email_from: str = ""
    notification_email_to: str = ""
    notification_email_password: str = ""
    notification_webhook_url: str = ""


# --- Config File Models ---


class BusinessHours(BaseModel):
    timezone: str = "Asia/Singapore"
    weekdays: str | None = "09:00-18:00"
    saturday: str | None = "09:00-13:00"
    sunday: str | None = None


class EmergencyContact(BaseModel):
    name: str
    phone: str


class CompanyConfig(BaseModel):
    company_name: str
    greeting: str
    business_hours: BusinessHours
    after_hours_message: str
    emergency_contact: EmergencyContact


class StaffMember(BaseModel):
    name: str
    role: str
    department: str
    phone: str
    email: str = ""


class DirectoryConfig(BaseModel):
    staff: list[StaffMember]


class SpamCategory(BaseModel):
    keywords: list[str]
    action: str = "decline"  # "decline" or "hang_up"
    detect_ai_voice: bool = False


class RepeatCallerConfig(BaseModel):
    window_minutes: int = 30
    max_calls_before_block: int = 2
    block_duration_hours: int = 24
    auto_add_to_blocked: bool = True


class SpamRulesConfig(BaseModel):
    blocked_numbers: list[str] = Field(default_factory=list)
    spam_categories: dict[str, SpamCategory] = Field(default_factory=dict)
    repeat_caller: RepeatCallerConfig = Field(default_factory=RepeatCallerConfig)
    decline_message: str = "We're not interested, thank you. Goodbye."


# --- ElevenLabs Tool Request/Response Models ---


class CheckCallerRequest(BaseModel):
    caller_number: str


class CheckCallerResponse(BaseModel):
    blocked: bool = False
    is_repeat_offender: bool = False
    known_contact: str | None = None
    action: str | None = None  # "allow", "decline", "hang_up"


class ReportSpamRequest(BaseModel):
    caller_number: str
    reason: str = ""


class ReportSpamResponse(BaseModel):
    logged: bool = True
    blocked: bool = False
    message: str = ""


class LookupStaffRequest(BaseModel):
    query: str  # person name only


class LookupStaffResponse(BaseModel):
    found: bool = False
    name: str = ""
    role: str = ""
    department: str = ""
    phone: str = ""
    email: str = ""
    available: bool = False
    message: str = ""


class TransferCallRequest(BaseModel):
    destination_number: str
    caller_message: str = "Please hold while I transfer you."
    reason: str = ""


class TransferCallResponse(BaseModel):
    success: bool = False
    message: str = ""


class TakeMessageRequest(BaseModel):
    caller_name: str
    caller_company: str = ""
    caller_phone: str
    caller_email: str = ""
    message: str
    intended_recipient: str = ""
    staff_email: str = ""


class TakeMessageResponse(BaseModel):
    success: bool = False
    message: str = ""
