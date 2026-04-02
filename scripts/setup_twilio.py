"""One-time script to configure a Twilio phone number for ElevenLabs integration.

Usage:
    python -m scripts.setup_twilio

When using ElevenLabs' native Twilio integration, you import the Twilio number
into ElevenLabs dashboard and it auto-configures webhooks. This script helps
verify the setup and optionally configure the call status callback.

Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

    if not all([account_sid, auth_token, phone_number]):
        print("Error: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER must be set in .env")
        sys.exit(1)

    from twilio.rest import Client

    client = Client(account_sid, auth_token)

    # Find the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=phone_number)

    if not numbers:
        print(f"Error: Phone number {phone_number} not found in your Twilio account.")
        print("Purchase a number first at https://console.twilio.com/")
        sys.exit(1)

    number = numbers[0]
    print(f"Found Twilio number: {number.phone_number} (SID: {number.sid})")
    print(f"  Voice URL: {number.voice_url}")
    print(f"  Status callback: {number.status_callback}")

    # Set the status callback to our backend
    status_url = f"{backend_url}/webhooks/call-status"
    number.update(status_callback=status_url)
    print(f"\nUpdated status callback to: {status_url}")

    print("\n--- Next Steps ---")
    print("1. Go to ElevenLabs dashboard → Telephony → Phone Numbers → Import")
    print(f"2. Import your Twilio number: {phone_number}")
    print(f"3. Enter Twilio Account SID: {account_sid}")
    print("4. Enter Twilio Auth Token: (from your .env)")
    print("5. Assign your AI agent to this phone number")
    print("6. ElevenLabs will auto-configure the voice webhook on Twilio")

    print("\n--- Singtel Call Forwarding ---")
    print(f"On your Singtel landline, activate call forwarding to {phone_number}:")
    print(f"  Dial: *72{phone_number.replace('+', '')}")
    print(f"  Or: **21*{phone_number.replace('+', '')}#")
    print("To deactivate: *73 or ##21#")


if __name__ == "__main__":
    main()
