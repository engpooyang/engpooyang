"""Tracks recent calls per number for repeat offender detection and auto-blocking."""

from __future__ import annotations

import json
import pathlib
import threading
import time

from src.services.config_loader import get_spam_rules_config

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "data"
BLOCKED_RUNTIME_FILE = DATA_DIR / "blocked_numbers_runtime.json"

_lock = threading.Lock()

# In-memory store: {phone_number: [timestamp, timestamp, ...]}
_recent_spam_calls: dict[str, list[float]] = {}

# Runtime blocked numbers (separate from config, auto-populated)
_runtime_blocked: dict[str, float] = {}  # {number: blocked_until_timestamp}


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_runtime_blocked() -> None:
    """Load runtime blocked numbers from disk."""
    global _runtime_blocked
    _ensure_data_dir()
    if BLOCKED_RUNTIME_FILE.exists():
        with open(BLOCKED_RUNTIME_FILE) as f:
            _runtime_blocked = json.load(f)


def _save_runtime_blocked() -> None:
    """Persist runtime blocked numbers to disk."""
    _ensure_data_dir()
    with open(BLOCKED_RUNTIME_FILE, "w") as f:
        json.dump(_runtime_blocked, f, indent=2)


def is_blocked(phone_number: str) -> bool:
    """Check if a number is blocked (config or runtime)."""
    config = get_spam_rules_config()

    # Check static blocked list from config
    if phone_number in config.blocked_numbers:
        return True

    # Check runtime blocked list
    with _lock:
        if not _runtime_blocked:
            _load_runtime_blocked()

        if phone_number in _runtime_blocked:
            blocked_until = _runtime_blocked[phone_number]
            if time.time() < blocked_until:
                return True
            # Block expired, remove it
            del _runtime_blocked[phone_number]
            _save_runtime_blocked()

    return False


def is_repeat_offender(phone_number: str) -> bool:
    """Check if a number has been flagged as spam multiple times recently."""
    config = get_spam_rules_config()
    window = config.repeat_caller.window_minutes * 60
    threshold = config.repeat_caller.max_calls_before_block
    now = time.time()

    with _lock:
        calls = _recent_spam_calls.get(phone_number, [])
        # Filter to only calls within the window
        recent = [t for t in calls if now - t < window]
        return len(recent) >= threshold


def record_spam_call(phone_number: str) -> bool:
    """Record a spam call. Returns True if the number was auto-blocked."""
    config = get_spam_rules_config()
    now = time.time()
    window = config.repeat_caller.window_minutes * 60

    with _lock:
        # Add to recent calls
        if phone_number not in _recent_spam_calls:
            _recent_spam_calls[phone_number] = []
        _recent_spam_calls[phone_number].append(now)

        # Clean old entries
        _recent_spam_calls[phone_number] = [
            t for t in _recent_spam_calls[phone_number] if now - t < window
        ]

        # Check if we should auto-block
        if (
            config.repeat_caller.auto_add_to_blocked
            and len(_recent_spam_calls[phone_number])
            >= config.repeat_caller.max_calls_before_block
        ):
            block_until = now + (config.repeat_caller.block_duration_hours * 3600)
            _runtime_blocked[phone_number] = block_until
            _save_runtime_blocked()
            return True

    return False


def get_blocked_numbers() -> list[str]:
    """Return all currently blocked numbers (config + runtime)."""
    config = get_spam_rules_config()
    now = time.time()

    with _lock:
        if not _runtime_blocked:
            _load_runtime_blocked()

        runtime = [n for n, until in _runtime_blocked.items() if now < until]

    return list(set(config.blocked_numbers + runtime))
