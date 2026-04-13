"""Serverless ElevenLabs agent setup — no backend required.

Embeds the staff directory directly into the agent's system prompt,
removes all custom webhook tools, and keeps only ElevenLabs built-in
system tools (Transfer-to-Number, End Call).

Message-taking is handled by ElevenLabs post-call webhook → Zapier (or Make.com)
→ email to staff. Configure the post-call webhook separately in the ElevenLabs
dashboard under Agent Settings → Post-Call Webhooks.

Usage:
    python -m scripts.setup_agent_serverless

Requires in .env:
    ELEVENLABS_API_KEY
    ELEVENLABS_AGENT_ID
"""

from __future__ import annotations

import os
import sys

import httpx
import yaml
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.elevenlabs.io"


SYSTEM_PROMPT_TEMPLATE = """You are Ava, the AI receptionist for {company_name}.

## Your job
1. Greet callers professionally.
2. Screen out spam/unwanted calls quickly.
3. Transfer legitimate callers to the right staff member by name.
4. If you cannot transfer, collect their contact details so we can call them back.

## Greeting
Start with: "Hello, thank you for calling {company_name}. How may I help you?"
Keep it brief — do not introduce yourself as AI unless asked.

## Spam handling (decline fast — do NOT engage)
If the caller is offering or discussing ANY of the following, treat as spam:
- Sales pitches, promotions, marketing offers, business partnerships
- Loans, credit, financing, mortgages, debt consolidation, investment offers
- Insurance of any kind (life, health, medical, vehicle)
- SEO, digital marketing, lead generation, website services
- "You have won", "free prize", "claim your reward"
- Press-1-to-continue style robocalls, scripted or synthetic-sounding voices
- Any unsolicited service or product

Response for spam:
Say exactly: "We're not interested, thank you. Goodbye."
Then immediately use the `end_call` system tool. Do NOT argue, explain, or ask follow-ups.

## Legitimate calls — transfer by name
If the caller asks to speak to a specific person by name, find that person in the
**Staff Directory** below. Match on full name, first name, last name, or nickname
(the name in parentheses).

When you find a match during business hours:
1. Say: "One moment please, I'll transfer you to [Name]."
2. Use the `transfer_to_number` system tool with that person's phone number.

If you find a match but outside business hours (see Business Hours below):
- Say: "[Name] is not available right now. Our office is currently closed.
  May I take your details and have them call you back?"
- Then follow the "Taking a callback request" section below.

If the caller asks for a **department** or **role** (e.g., "someone in support",
"your sales team"), DO NOT guess. Say:
"I can only transfer to a specific person by name. May I take your details
and have the right person call you back?"
Then follow the "Taking a callback request" section.

## Taking a callback request
When you cannot transfer (no name match, caller has no specific person, or
after-hours), collect:
1. Caller's full name
2. Caller's company (if any)
3. Caller's phone number — read it back to confirm
4. Caller's email (optional, but ask)
5. Who they want to speak with (name if known, or purpose of call)
6. A brief message or reason for the call

Then say: "Thank you. I've recorded your details and the team will call you
back as soon as possible. Have a good day."

Then use the `end_call` system tool.

(The conversation transcript is automatically emailed to our team after the
call ends — you do NOT need to call any tool to send the message.)

## Emergency calls
If the caller says it is urgent/emergency, transfer immediately to:
{emergency_contact_name} at {emergency_contact_phone}

## Business Hours ({business_timezone})
- Weekdays: {weekdays}
- Saturday: {saturday}
- Sunday: {sunday}

Today's day and time are provided in the system context.

## Staff Directory
When someone asks for a person by name, match them to this list and transfer
to the phone number shown. Match intelligently — "Junie" matches "Lek Yam Joo (Junie)",
"Darius" matches "Chen Guizhong (Darius)", etc.

{staff_directory}

## Rules
- NEVER read out internal phone numbers or email addresses to callers.
- NEVER engage with spam callers beyond the single decline sentence.
- Keep all responses concise — you are on a phone call, not chatting.
- If unsure whether a call is legitimate, err on the side of taking a message
  rather than transferring.
- Always end the call cleanly with the `end_call` system tool.
"""


def format_staff_directory(directory_path: str) -> str:
    """Format the staff directory YAML into a readable prompt section."""
    with open(directory_path) as f:
        data = yaml.safe_load(f)

    lines = []
    for staff in data.get("staff", []):
        lines.append(
            f"- **{staff['name']}** — {staff['role']} ({staff['department']})\n"
            f"  Phone: {staff['phone']} | Email: {staff.get('email', '')}"
        )
    return "\n".join(lines)


def build_system_prompt() -> str:
    with open("config/company.yml") as f:
        company = yaml.safe_load(f)

    staff_dir = format_staff_directory("config/directory.yml")

    bh = company["business_hours"]
    return SYSTEM_PROMPT_TEMPLATE.format(
        company_name=company["company_name"],
        emergency_contact_name=company["emergency_contact"]["name"],
        emergency_contact_phone=company["emergency_contact"]["phone"],
        business_timezone=bh["timezone"],
        weekdays=bh.get("weekdays") or "closed",
        saturday=bh.get("saturday") or "closed",
        sunday=bh.get("sunday") or "closed",
        staff_directory=staff_dir,
    )


def build_transfer_rules(directory_path: str) -> list[dict]:
    """Build transfer_to_number rules — one entry per staff member."""
    with open(directory_path) as f:
        data = yaml.safe_load(f)

    transfers = []
    for staff in data.get("staff", []):
        transfers.append(
            {
                "transfer_type": "conference",
                "phone_number": staff["phone"],
                "condition": (
                    f"Caller asks to speak with {staff['name']} "
                    f"({staff['role']}, {staff['department']} department). "
                    f"Match on full name, first name, last name, or nickname."
                ),
            }
        )
    return transfers


def update_agent(api_key: str, agent_id: str, prompt: str) -> None:
    """PATCH the agent to use the new prompt and strip custom webhook tools.

    - Removes all custom webhook tools (tool_ids + inline webhook definitions)
    - Preserves existing system tools (end_call, language_detection)
    - Configures transfer_to_number with staff directory destinations
    """
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    r = httpx.get(f"{API_BASE}/v1/convai/agents/{agent_id}", headers=headers, timeout=30)
    r.raise_for_status()
    agent = r.json()

    conv_cfg = agent.get("conversation_config", {})
    agent_cfg = conv_cfg.get("agent", {})
    prompt_cfg = agent_cfg.get("prompt", {})

    # 1. Update the system prompt
    prompt_cfg["prompt"] = prompt

    # 2. Remove all custom webhook tool_ids
    prompt_cfg["tool_ids"] = []

    # 3. Filter tools: keep only system tools, drop webhook tools
    existing_tools = prompt_cfg.get("tools", [])
    kept = [t for t in existing_tools if t.get("type") == "system"]

    # 4. Add transfer_to_number via built_in_tools (correct location for system tools)
    built_in = prompt_cfg.get("built_in_tools") or {}
    transfer_tool = {
        "type": "system",
        "name": "transfer_to_number",
        "description": "",
        "response_timeout_secs": 20,
        "disable_interruptions": False,
        "force_pre_tool_speech": False,
        "assignments": [],
        "params": {
            "system_tool_type": "transfer_to_number",
            "transfers": build_transfer_rules("config/directory.yml"),
        },
    }
    built_in["transfer_to_number"] = transfer_tool
    prompt_cfg["built_in_tools"] = built_in

    # Also add to tools array for redundancy (ElevenLabs keeps both in sync)
    kept = [t for t in kept if t.get("name") != "transfer_to_number"]
    kept.append(transfer_tool)
    prompt_cfg["tools"] = kept

    agent_cfg["prompt"] = prompt_cfg
    conv_cfg["agent"] = agent_cfg

    # 5. Minimize the workflow — keep only a start node so the main agent
    # prompt handles the entire conversation (no per-node overrides).
    payload = {
        "conversation_config": conv_cfg,
        "workflow": {
            "nodes": {
                "start_node": {
                    "type": "start",
                    "position": {"x": 400.0, "y": 0.0},
                    "edge_order": [],
                }
            },
            "edges": {},
            "prevent_subagent_loops": True,
        },
    }

    r = httpx.patch(
        f"{API_BASE}/v1/convai/agents/{agent_id}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if r.status_code >= 400:
        print(f"Error {r.status_code}: {r.text}")
        r.raise_for_status()

    print(f"Agent {agent_id} updated — serverless mode enabled.")
    print(f"  - Custom webhook tools removed (tool_ids cleared)")
    print(f"  - Workflow cleared — single-agent mode")
    print(f"  - System tools: end_call, language_detection, transfer_to_number")
    print(f"  - Transfer destinations: {len(transfer_tool['params']['transfers'])} staff members")


def main() -> None:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")

    if not api_key:
        print("Error: ELEVENLABS_API_KEY not set in .env")
        sys.exit(1)
    if not agent_id:
        print("Error: ELEVENLABS_AGENT_ID not set in .env")
        sys.exit(1)

    prompt = build_system_prompt()

    print("=" * 70)
    print("SERVERLESS AGENT SETUP")
    print("=" * 70)
    print(f"Agent: {agent_id}")
    print(f"Prompt length: {len(prompt)} chars")
    print()
    print("This will:")
    print("  1. Embed the full staff directory in the agent prompt")
    print("  2. Remove all custom webhook tools (tool_ids cleared)")
    print("  3. Keep only built-in: transfer_to_number, end_call")
    print()

    update_agent(api_key, agent_id, prompt)

    print()
    print("=" * 70)
    print("NEXT: Configure Post-Call Webhook for message emails")
    print("=" * 70)
    print("""
1. Create a Zapier account (free): https://zapier.com
2. Create a new Zap:
   - Trigger: "Webhooks by Zapier" → "Catch Hook"
   - Copy the webhook URL Zapier generates
3. Add action: "Gmail" → "Send Email"
   - To: (use Zapier's AI/Formatter to extract the staff email from the
     transcript, or route to a central ops@appvantage.asia inbox)
   - Subject: "Callback request from {{caller}} via AI receptionist"
   - Body: include the full transcript {{transcript}}
4. In ElevenLabs dashboard:
   - Agent Settings → Post-Call Webhooks
   - Paste the Zapier Catch Hook URL
   - Enable it

Alternative: Use Make.com (free tier, similar flow) if you prefer.
""")


if __name__ == "__main__":
    main()
