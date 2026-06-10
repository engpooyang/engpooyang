"""Poll ElevenLabs for recent calls and email summaries to staff.

Bypasses the Zapier webhook field-mapping issue by reading conversation
data directly from the ElevenLabs API and sending formatted emails via
the Zapier Catch Hook with flat top-level fields.

Usage:
    python -m scripts.email_notifier          # one-shot check
    python -m scripts.email_notifier --loop    # poll every 60s

Requires in .env:
    ELEVENLABS_API_KEY
    ELEVENLABS_AGENT_ID
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

API = "https://api.elevenlabs.io"
AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
API_KEY = os.getenv("ELEVENLABS_API_KEY")
HEADERS = {"xi-api-key": API_KEY}
ZAPIER_HOOK = "https://hooks.zapier.com/hooks/catch/27197951/u7c5mjz/"
STATE_FILE = Path(__file__).parent.parent / ".notifier_state.json"
DEFAULT_EMAIL = "pooyang@appvantage.asia"


def load_state() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_state(seen: set[str]) -> None:
    recent = sorted(seen)[-200:]
    STATE_FILE.write_text(json.dumps(recent))


def get_recent_conversations(client: httpx.Client, limit: int = 10) -> list[dict]:
    r = client.get(
        f"{API}/v1/convai/conversations",
        params={"agent_id": AGENT_ID, "page_size": limit},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("conversations", [])


def get_conversation_detail(client: httpx.Client, conv_id: str) -> dict:
    r = client.get(
        f"{API}/v1/convai/conversations/{conv_id}",
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def send_email_via_zapier(client: httpx.Client, payload: dict) -> bool:
    r = client.post(ZAPIER_HOOK, json=payload, timeout=30)
    return r.status_code == 200


def process_conversation(client: httpx.Client, conv: dict) -> bool:
    conv_id = conv["conversation_id"]
    detail = get_conversation_detail(client, conv_id)

    analysis = detail.get("analysis", {})
    dcr = analysis.get("data_collection_results", {})

    def val(key: str) -> str:
        entry = dcr.get(key, {})
        v = entry.get("value") if isinstance(entry, dict) else entry
        return v or ""

    caller_name = val("caller_name")
    caller_company = val("caller_company")
    contact_number = val("contact_number")
    purpose = val("call_purpose_summary")
    classification = val("call_classification")
    transfer_status = val("transfer_status")
    intended_recipient = val("intended_recipient")
    recipient_email = val("recipient_email")
    transcript_summary = analysis.get("transcript_summary", "")

    if not recipient_email or recipient_email == "spam":
        recipient_email = DEFAULT_EMAIL

    if classification == "spam_unimportant" and transfer_status == "filtered_out":
        print(f"  Skipping {conv_id} — spam/filtered")
        return True

    payload = {
        "type": "post_call_transcription",
        "caller_name": caller_name,
        "caller_company": caller_company,
        "contact_number": contact_number,
        "call_purpose_summary": purpose,
        "call_classification": classification,
        "transfer_status": transfer_status,
        "intended_recipient": intended_recipient,
        "recipient_email": recipient_email,
        "transcript_summary": transcript_summary,
        "conversation_id": conv_id,
    }

    ok = send_email_via_zapier(client, payload)
    if ok:
        print(f"  Sent email for {conv_id} → {recipient_email}")
        print(f"    caller={caller_name}, company={caller_company}, status={transfer_status}")
    else:
        print(f"  FAILED to send for {conv_id}")
    return ok


def run_once(client: httpx.Client) -> int:
    seen = load_state()
    convs = get_recent_conversations(client)
    new_count = 0

    for c in convs:
        cid = c["conversation_id"]
        status = c.get("status", "")
        if cid in seen:
            continue
        if status != "done":
            continue

        print(f"Processing {cid}...")
        try:
            process_conversation(client, c)
            new_count += 1
        except Exception as e:
            print(f"  Error: {e}")
        seen.add(cid)

    save_state(seen)
    return new_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Poll continuously")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between polls")
    args = parser.parse_args()

    client = httpx.Client(verify=False)

    if args.loop:
        print(f"Polling every {args.interval}s. Ctrl+C to stop.")
        while True:
            try:
                n = run_once(client)
                if n:
                    print(f"Processed {n} new conversations")
            except Exception as e:
                print(f"Poll error: {e}")
            time.sleep(args.interval)
    else:
        n = run_once(client)
        print(f"Done. Processed {n} new conversations.")


if __name__ == "__main__":
    main()
