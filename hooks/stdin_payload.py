from __future__ import annotations

import json
import sys
from typing import Any

from core.errors import HookPayloadError


def read_hook_payload(raw_text: str | None = None) -> dict[str, Any]:
    payload_text = sys.stdin.read() if raw_text is None else raw_text
    if not payload_text.strip():
        raise HookPayloadError("Received an empty Claude hook payload.")

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise HookPayloadError("Claude hook payload was not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise HookPayloadError("Claude hook payload must decode to an object.")

    return payload


def get_tool_name(payload: dict[str, Any]) -> str | None:
    for key in ("tool_name", "tool"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return None
