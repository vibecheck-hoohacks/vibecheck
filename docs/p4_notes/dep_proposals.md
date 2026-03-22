# Dependency Proposals

Proposals only — not installed or implemented. Each has a rationale, what it replaces, and scope of change.

## 1. `rich` — Terminal UX Enhancement

**Rationale**: The terminal renderer currently uses plain `print()` to stderr with manual separator bars and Unicode characters. `rich` would provide:
- Syntax-highlighted code in faded_example prompts (critical for users reading code in terminal)
- Colored pass/fail feedback (green checkmark, red X)
- Panel/box rendering for visual separation
- Progress indicators for QA loop state

**What it replaces**: Manual `_SEPARATOR` bars, plain text formatting in `qa/terminal_renderer.py`

**Scope of change**: Only `qa/terminal_renderer.py`. No core logic changes. Would become an optional dependency (terminal still works without it, just less pretty).

**Verdict**: RECOMMEND — genuine QoL improvement for the primary UX path. The terminal is the default renderer and most users will interact through it.

## 2. `pydantic` — Structured Validation at Boundaries

**Rationale**: Hook payloads arrive as untyped JSON dicts. Currently validated with manual `isinstance()` checks and `HookPayloadError` raises. Pydantic would:
- Auto-validate hook payloads with clear error messages
- Provide serialization/deserialization for state artifacts
- Replace manual dict-to-dataclass conversion in `core/competence_store.py`

**What it replaces**: Manual validation in `hooks/stdin_payload.py`, manual YAML-to-dataclass in `core/competence_store.py`

**Scope of change**: Medium — would touch `core/models.py` (convert dataclasses to Pydantic models), `hooks/stdin_payload.py`, `core/competence_store.py`. Does NOT affect core gate or QA logic.

**Verdict**: DEFER — the current dataclass approach works. Pydantic adds weight. Worth considering if/when the LLM adapter needs structured output validation, since LangChain's `with_structured_output()` works well with Pydantic models.

## 3. `structlog` — Structured Event Logging

**Rationale**: The hand-rolled `EventLogger` in `core/event_logger.py` works but is minimal. `structlog` would provide:
- Structured key-value logging with consistent formatting
- Log level filtering
- Processor pipeline for enrichment
- Better debugging output

**What it replaces**: `core/event_logger.py` custom JSONL logger

**Scope of change**: Small — only `core/event_logger.py` internals. The `EventLogger` API surface would stay the same.

**Verdict**: DEFER — the current logger is 60 lines and does exactly what's needed. `structlog` is better for production systems with multiple log consumers. Revisit when/if VibeCheck moves beyond local MVP.

## 4. `click` or `typer` — CLI Entrypoint

**Rationale**: `hooks/pre_tool_use.py:main()` reads stdin and writes stdout. If VibeCheck grows subcommands (e.g., `vibecheck replay`, `vibecheck status`, `vibecheck reset-competence`), a CLI framework would help.

**What it replaces**: The bare `if __name__ == "__main__"` entrypoint

**Scope of change**: Small initially — wrap existing `main()`. Grows with subcommands.

**Verdict**: DEFER — premature for MVP. Only one entrypoint exists. Revisit when a second subcommand is needed.

## Summary

| Dependency | Verdict | Priority |
|-----------|---------|----------|
| `rich` | RECOMMEND | High (terminal is primary UX) |
| `pydantic` | DEFER | Medium (useful when LLM adapter lands) |
| `structlog` | DEFER | Low (current logger is sufficient) |
| `click`/`typer` | DEFER | Low (only one entrypoint) |
