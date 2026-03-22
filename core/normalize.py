from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from core.diffs import build_unified_diff, count_diff_stats, detect_language
from core.errors import HookPayloadError, UnsupportedMutationError
from core.models import ChangeProposal, ChangeTarget

CODE_MUTATION_TOOLS = frozenset({"Edit", "MultiEdit", "NotebookEdit", "Write"})


def is_code_mutation_tool(tool_name: str | None) -> bool:
    return tool_name in CODE_MUTATION_TOOLS


def normalize_mutation_payload(payload: Mapping[str, Any]) -> ChangeProposal:
    tool_name = _first_string(payload, "tool_name", "tool")
    if not is_code_mutation_tool(tool_name):
        raise UnsupportedMutationError(f"Unsupported mutation tool: {tool_name!r}")

    raw_input = payload.get("tool_input") or payload.get("input") or {}
    if not isinstance(raw_input, Mapping):
        raise HookPayloadError("Expected tool input to be an object.")

    targets = _normalize_targets(raw_input)
    diffs = [
        build_unified_diff(target.old_content, target.new_content, target.path)
        for target in targets
    ]
    unified_diff_text = "\n".join(diff for diff in diffs if diff)

    return ChangeProposal(
        proposal_id=str(payload.get("proposal_id") or f"proposal-{uuid4().hex}"),
        session_id=str(payload.get("session_id") or "unknown_session"),
        tool_use_id=str(payload.get("tool_use_id") or f"tool-{uuid4().hex}"),
        tool_name=tool_name,
        cwd=str(payload.get("cwd") or "."),
        targets=targets,
        unified_diff=unified_diff_text,
        diff_stats=count_diff_stats(unified_diff_text, files_changed=len(targets)),
        created_at=_utc_now_iso(),
    )


def _normalize_targets(raw_input: Mapping[str, Any]) -> list[ChangeTarget]:
    if "targets" in raw_input:
        raw_targets = raw_input["targets"]
        if not isinstance(raw_targets, Sequence) or isinstance(raw_targets, str):
            raise HookPayloadError("Expected targets to be a list of file mutations.")
        return [_build_target(target) for target in raw_targets]

    return [_build_target(raw_input)]


def _build_target(raw_target: Any) -> ChangeTarget:
    if not isinstance(raw_target, Mapping):
        raise HookPayloadError("Each target must be an object.")

    path = str(raw_target.get("path") or raw_target.get("file_path") or "")
    if not path:
        raise HookPayloadError("Mutation target is missing a file path.")

    new_content = raw_target.get("new_content")
    if new_content is None:
        new_content = raw_target.get("content")
    if not isinstance(new_content, str):
        raise HookPayloadError("Mutation target is missing new content.")

    old_content = raw_target.get("old_content")
    if old_content is not None and not isinstance(old_content, str):
        raise HookPayloadError("old_content must be a string when provided.")

    return ChangeTarget(
        path=path,
        language=detect_language(path),
        old_content=old_content,
        new_content=new_content,
    )


def _first_string(payload: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    raise HookPayloadError(f"Expected one of {keys!r} in hook payload.")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
