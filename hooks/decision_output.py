from __future__ import annotations

import json
from typing import Any, Literal

HookDecision = Literal["allow", "deny"]


def allow_response(reason: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return _decision_response("allow", reason, metadata)


def deny_response(reason: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return _decision_response("deny", reason, metadata)


def emit_decision(response: dict[str, Any]) -> None:
    print(json.dumps(response))


def _decision_response(
    decision: HookDecision,
    reason: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    if metadata:
        response["metadata"] = metadata
    return response
