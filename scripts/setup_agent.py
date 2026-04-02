"""One-time script to create or update the ElevenLabs AI agent.

Usage:
    python -m scripts.setup_agent

Requires ELEVENLABS_API_KEY and BACKEND_URL in .env
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

SYSTEM_PROMPT = """You are a professional receptionist for {company_name}.

When greeting callers:
- Be brief and professional
- Immediately check the caller using the check_caller tool

When handling spam/unwanted calls:
- Sales pitches, loan offers, insurance offers, promotions → decline immediately
- AI robocalls ("press 1", scripted responses) → hang up immediately
- Say only: "We're not interested, thank you. Goodbye." then report_spam and end call
- Do NOT engage in back-and-forth with spam callers

When handling legitimate calls:
- Ask who they'd like to speak with
- Use lookup_staff to find the right person
- Transfer if available; take a message if not
- For emergencies, always transfer to {emergency_contact_name} at {emergency_contact_phone}

Rules:
- Never reveal internal phone numbers
- Keep calls concise
"""


def build_tool_config(backend_url: str, api_secret: str) -> list[dict]:
    """Build the custom server tools configuration for the agent."""
    headers = {}
    if api_secret:
        headers["Authorization"] = f"Bearer {api_secret}"

    tools = [
        {
            "type": "webhook",
            "name": "check_caller",
            "description": "Check if a caller's phone number is blocked, a repeat spam offender, or a known contact. Call this immediately when answering.",
            "webhook": {
                "url": f"{backend_url}/tools/check-caller",
                "method": "POST",
                "headers": headers,
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_number": {
                        "type": "string",
                        "description": "The caller's phone number in E.164 format",
                    }
                },
                "required": ["caller_number"],
            },
        },
        {
            "type": "webhook",
            "name": "report_spam",
            "description": "Report a caller as spam. If they call repeatedly, their number will be auto-blocked. Use this when declining spam/sales/loan/insurance calls.",
            "webhook": {
                "url": f"{backend_url}/tools/report-spam",
                "method": "POST",
                "headers": headers,
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_number": {
                        "type": "string",
                        "description": "The spam caller's phone number",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief reason for flagging (e.g., 'loan offer', 'sales call')",
                    },
                },
                "required": ["caller_number"],
            },
        },
        {
            "type": "webhook",
            "name": "lookup_staff",
            "description": "Find a staff member by name or department. Returns their availability and transfer number.",
            "webhook": {
                "url": f"{backend_url}/tools/lookup-staff",
                "method": "POST",
                "headers": headers,
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Name or department to search for",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "type": "webhook",
            "name": "transfer_call",
            "description": "Get the transfer destination to hand off the call to a staff member.",
            "webhook": {
                "url": f"{backend_url}/tools/transfer-call",
                "method": "POST",
                "headers": headers,
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_number": {
                        "type": "string",
                        "description": "Phone number to transfer to",
                    },
                    "caller_message": {
                        "type": "string",
                        "description": "Message to tell the caller while transferring",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the transfer",
                    },
                },
                "required": ["destination_number"],
            },
        },
        {
            "type": "webhook",
            "name": "take_message",
            "description": "Record a message from the caller and notify the team. Use when staff is unavailable or after business hours.",
            "webhook": {
                "url": f"{backend_url}/tools/take-message",
                "method": "POST",
                "headers": headers,
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_name": {
                        "type": "string",
                        "description": "Name of the caller",
                    },
                    "caller_company": {
                        "type": "string",
                        "description": "Caller's company name",
                    },
                    "caller_phone": {
                        "type": "string",
                        "description": "Caller's phone number",
                    },
                    "message": {
                        "type": "string",
                        "description": "The message content",
                    },
                    "intended_recipient": {
                        "type": "string",
                        "description": "Who the message is for",
                    },
                },
                "required": ["caller_name", "caller_phone", "message"],
            },
        },
    ]
    return tools


def main() -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not set in .env")
        sys.exit(1)

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    api_secret = os.getenv("API_SECRET_KEY", "")

    client = ElevenLabs(api_key=api_key)
    tools = build_tool_config(backend_url, api_secret)

    # Load company config for the system prompt
    import yaml

    with open("config/company.yml") as f:
        company = yaml.safe_load(f)

    prompt = SYSTEM_PROMPT.format(
        company_name=company["company_name"],
        emergency_contact_name=company["emergency_contact"]["name"],
        emergency_contact_phone=company["emergency_contact"]["phone"],
    )

    agent_id = os.getenv("ELEVENLABS_AGENT_ID")

    if agent_id:
        print(f"Updating existing agent: {agent_id}")
        # Note: Update API may vary — check ElevenLabs SDK docs for exact method
        print("Agent update requires manual dashboard configuration or API v2.")
        print(f"System prompt:\n{prompt}")
        print(f"\nTools config ({len(tools)} tools):")
        for t in tools:
            print(f"  - {t['name']}: {t['webhook']['url']}")
    else:
        print("Creating new agent...")
        print("Note: Agent creation via API — check ElevenLabs SDK for exact method.")
        print(f"\nSystem prompt:\n{prompt}")
        print(f"\nTools config ({len(tools)} tools):")
        for t in tools:
            print(f"  - {t['name']}: {t['webhook']['url']}")
        print("\nCopy the above configuration into your ElevenLabs dashboard")
        print("or use the ElevenLabs API to create the agent programmatically.")


if __name__ == "__main__":
    main()
