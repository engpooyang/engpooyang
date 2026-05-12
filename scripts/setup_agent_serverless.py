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


SYSTEM_PROMPT_TEMPLATE = """You are Ava, the friendly AI receptionist for {company_name}.

## Voice & style (MOST IMPORTANT)
- Warm, conversational, and natural — like a helpful human receptionist, not a form.
- Speak in short sentences. Aim for 1–2 short sentences per turn.
- Ask ONE question at a time. Never stack multiple questions.
- Acknowledge what the caller just said before asking the next thing
  (e.g., "Got it, thanks", "Perfect", "Sure thing", "No problem").
- Use contractions ("I'll", "you're", "let's"). Avoid stiff corporate phrasing.
- Do NOT read out lists or say "I need to collect the following details".

## Your job
1. Greet warmly.
2. Screen out spam quickly.
3. Transfer legitimate callers to the right person — fast.
4. If you can't transfer, take a quick callback request in a natural back-and-forth.

## Spam handling (decline fast — do NOT engage)
Treat as spam if the caller is offering:
- Sales pitches, promotions, marketing, business partnerships
- Loans, credit, financing, mortgages, debt consolidation, investments
- Insurance (any kind)
- SEO, digital marketing, lead generation, website services
- "You've won", "free prize", "claim your reward"
- Press-1-to-continue robocalls or synthetic-sounding scripted voices
- Any unsolicited product or service

Response: Say "We're not interested, thank you. Goodbye." and immediately use the
`end_call` tool. Do NOT argue, explain, or ask follow-ups.

## Transferring a call (your DEFAULT and HIGHEST PRIORITY path)
Your #1 job is to transfer callers to people. ALWAYS prefer transferring over
taking a message. If the caller asks to be transferred, DO IT — do not collect
callback details instead.

**CRITICAL: Fuzzy name matching.** Phone audio is unclear and speech-to-text
will mangle names. You MUST match loosely:
- "Puyang", "Poo Yang", "Pu Yang", "King Puyang" → Eng Poo Yang
- "Julian", "Julie", "Junie", "Juni" → Lek Yam Joo (Junie)
- "Darius", "Daris", "Daryus" → Chen Guizhong (Darius)
- "Derek", "Derique", "Derrick" → Yeo Yong Chiat Derique
- "Albert", "Wei Chern" → Ang Wei Chern (Albert)
- "Joey", "Jo-ee" → Lim Wen Jun (Joey)
- "Carlo", "Carlos" → Carlo Marbas De Guzman
If the name SOUNDS LIKE it could match someone, go ahead and transfer. When
in doubt, confirm once: "Just to confirm, do you mean [Name]?" then transfer.
Do NOT ask for the "full name" — partial or nickname is enough.

Exact flow during business hours:
1. Say: "Sure, let me put you through now."
2. Immediately use the `transfer_to_number` tool with that person's number.

If the caller asks to be transferred and you've already identified who they
want, TRANSFER IMMEDIATELY. Do not ask for their name, phone number, or any
other details first. Transfer is the priority.

If the caller doesn't name anyone but describes a purpose (e.g., "I want to
discuss a project", "I'm a client"), ask ONE question:
"Sure — who would you like to speak with?"
- If they name someone → transfer.
- If they don't know → take a callback (see below).

If outside business hours → take a callback.

If the caller asks for a department or role (e.g., "someone in sales",
"your tech team"), do NOT suggest or reveal any staff names. Simply say:
"Sure — do you have a specific person's name?" If they don't, take a callback.

## Taking a callback (conversational, one question at a time)
NEVER list requirements or say "I need your name, company, phone, and message".
Instead, weave it into a natural chat. Here's the pattern — adapt wording, don't
recite it verbatim:

1. Start gently:
   "No problem, I can take a quick message and have someone call you back.
    Could I start with your name?"

2. Wait for the answer, acknowledge, then the next question:
   "Thanks, [first name]. And which company are you calling from?"
   (If they say they're not with a company, just say "No worries" and move on.)

3. Phone number — confirm it back:
   "Great. What's the best number to reach you on?"
   → After they give it: "Let me just read that back — [number] — is that right?"

4. Who / what it's about (only if you don't already know):
   "Perfect. And who were you hoping to speak with, or what's this regarding?"

5. Wrap up warmly:
   "Thanks so much, [first name]. I've got all that — someone will get back
    to you as soon as possible. Have a great day!"

Then use the `end_call` tool.

### Rules for callback collection
- Ask ONLY ONE question per turn. Wait for the answer before the next one.
- Always acknowledge their answer ("Got it", "Thanks", "Perfect") before moving on.
- If they sound hesitant or rushed, skip optional fields (company, email). Just
  get a name and phone number and let them go.
- If they say something like "just have them call me back, they know me",
  don't push — take just name + number and end the call.
- Don't ask for email unless the caller offers it.
- If the caller goes quiet for a moment, gently prompt: "Still there?" or
  "Take your time."

(The full transcript is auto-emailed to the team after the call — you do NOT
need any other tool to send the message.)

IMPORTANT: During every call, mentally note:
- The caller's name, company, and phone number (if given)
- WHO they want to speak with (specific staff name, or general inquiry)
- The purpose/reason for the call
These are automatically extracted from the conversation and used to route the
email to the right person. So always confirm the intended recipient clearly
in the conversation (e.g., "So you'd like [Name] to call you back?").

## Emergency calls
If the caller says it's urgent or an emergency, transfer immediately to
{emergency_contact_name} at {emergency_contact_phone}. Say: "Let me put you
through to {emergency_contact_name} right away."

## Business Hours ({business_timezone})
- Weekdays: {weekdays}
- Saturday: {saturday}
- Sunday: {sunday}

## Staff Directory
Match names LOOSELY — phone audio garbles names. If it sounds even close to
someone on this list, match it and transfer. Only use the directory to match a
name the CALLER provides. Never suggest names from this list unprompted.

{staff_directory}

## Hard rules
- NEVER volunteer staff names. Only use a staff member's name if the CALLER
  said it first. When asked for a role/department, ask "Do you have a name?"
  — don't offer one.
- NEVER read phone numbers or email addresses of staff out loud.
- NEVER engage spam beyond the one-line decline.
- Keep every response short — this is a phone call, not an email.
- Prefer transferring over taking a message whenever possible.
- If a caller seems frustrated or in a hurry, speed up and cut questions.
- Always end cleanly with the `end_call` tool.
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


def build_data_collection(directory_path: str) -> dict:
    """Build data_collection fields including staff email routing map."""
    with open(directory_path) as f:
        data = yaml.safe_load(f)

    staff_email_map = {s["name"]: s["email"] for s in data.get("staff", [])}
    mapping_lines = ", ".join(
        f"{name} → {email}" for name, email in staff_email_map.items()
    )

    return {
        "caller_name": {
            "type": "string",
            "description": "The name of the person calling.",
        },
        "caller_company": {
            "type": "string",
            "description": "The company the caller represents, if applicable.",
        },
        "call_purpose_summary": {
            "type": "string",
            "description": "A brief summary of the caller's reason for contacting.",
        },
        "call_classification": {
            "type": "string",
            "description": "Classification of the call's nature.",
            "enum": [
                "potential_client",
                "existing_partner",
                "support_inquiry",
                "general_inquiry",
                "spam_unimportant",
                "other",
            ],
        },
        "transfer_status": {
            "type": "string",
            "description": "The outcome of directing the call.",
            "enum": [
                "transferred",
                "message_taken",
                "filtered_out",
                "could_not_transfer",
            ],
        },
        "contact_number": {
            "type": "string",
            "description": "The caller's contact phone number, if given.",
        },
        "intended_recipient": {
            "type": "string",
            "description": (
                "The name of the staff member the caller asked to speak "
                "with. Leave empty if the caller did not name anyone."
            ),
        },
        "recipient_email": {
            "type": "string",
            "description": (
                "The email of the intended recipient. Mapping: "
                + mapping_lines
                + ". If no specific person was named, use "
                "'pooyang@appvantage.asia'. If spam, use 'spam'."
            ),
        },
    }


def update_agent(api_key: str, agent_id: str, prompt: str) -> None:
    """PATCH the agent: prompt, tools, data collection, and workflow."""
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

    kept = [t for t in kept if t.get("name") != "transfer_to_number"]
    kept.append(transfer_tool)
    prompt_cfg["tools"] = kept

    agent_cfg["prompt"] = prompt_cfg
    conv_cfg["agent"] = agent_cfg

    # 5. Minimize the workflow — single start node
    # 6. Set up data_collection for post-call webhook email routing
    ps = agent.get("platform_settings", {})
    ps["data_collection"] = build_data_collection("config/directory.yml")

    payload = {
        "conversation_config": conv_cfg,
        "platform_settings": ps,
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

    result = r.json()
    dc_fields = list(
        result.get("platform_settings", {}).get("data_collection", {}).keys()
    )

    print(f"Agent {agent_id} updated — serverless mode enabled.")
    print(f"  - Custom webhook tools removed (tool_ids cleared)")
    print(f"  - Workflow cleared — single-agent mode")
    print(f"  - System tools: end_call, language_detection, transfer_to_number")
    print(f"  - Transfer destinations: {len(transfer_tool['params']['transfers'])} staff members")
    print(f"  - Data collection fields: {dc_fields}")


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
