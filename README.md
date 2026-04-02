# AI Landline Agent

AI-powered phone receptionist using ElevenLabs Conversational AI. Answers your company landline, screens spam calls, routes legitimate callers to the right staff, and takes messages when unavailable.

## Architecture

```
Caller -> Singtel Landline -> (call forward) -> Twilio Number -> ElevenLabs AI Agent -> Backend (FastAPI)
```

**Call filtering and routing** is managed via the ElevenLabs visual workflow builder -- adjust spam categories, routing branches, and agent behavior from the dashboard without code changes.

**Backend** handles data operations: blocked numbers, call logs, staff directory, and message notifications.

## Features

- Spam detection: sales calls, loan offers, insurance, scams, AI robocalls
- Repeat caller auto-blocking (configurable threshold and duration)
- Staff directory lookup by name or department
- Call transfer to staff with availability checking
- Message-taking with Slack/webhook notifications
- Business hours awareness (Singapore timezone)

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys
2. Edit `config/company.yml`, `config/directory.yml`, `config/spam_rules.yml`
3. Run:

```bash
docker-compose up --build
```

4. Run setup scripts:

```bash
python -m scripts.setup_agent    # Configure ElevenLabs agent
python -m scripts.setup_twilio   # Configure Twilio number
```

5. Activate Singtel call forwarding to your Twilio number

## Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
pytest tests/ -v
```

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /tools/check-caller` | Check caller against blocked/repeat list |
| `POST /tools/report-spam` | Log spam caller, auto-block repeats |
| `POST /tools/lookup-staff` | Find staff by name/department |
| `POST /tools/transfer-call` | Get transfer destination |
| `POST /tools/take-message` | Record message and notify |
| `GET /health` | Health check |
