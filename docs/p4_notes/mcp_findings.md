# MCP Docs Validation Findings

## PyYAML Usage — CORRECT

- `yaml.safe_load()` is the universally recommended API. No unsafe `yaml.load()` calls found.
- `yaml.safe_dump()` with `sort_keys=False` is correct and standard.
- `safe_load()` returns `None` for empty docs — already handled with `or {}` fallback in `core/competence_store.py:18`.
- No anti-patterns found.

## pytest Patterns — ONE ANTI-PATTERN

- **Anti-pattern found**: `tests/test_failure_modes.py` imports `FakeRenderer`, `_make_gate_decision`, and `_make_proposal` directly from `tests/test_qa_loop.py`. This is a known pytest anti-pattern — test modules should not import from each other.
- **Proposed fix**: Move `FakeRenderer`, `_make_proposal`, `_make_gate_decision` to `tests/conftest.py` as shared fixtures or helper functions. This is the pytest-recommended approach.
- `tmp_path` usage is correct and follows best practices (function-scoped, pathlib-based).
- `monkeypatch` usage for renderer mocking is appropriate.
- Replay fixture JSON files in `tests/fixtures/` is a valid pattern.

## Ruff Configuration — MOSTLY CORRECT

- Rule selection `["E", "F", "I", "UP", "B", "SIM"]` matches the Ruff tutorial's recommended baseline.
- Ignoring `E501` while setting `line-length = 100` is slightly redundant — `ruff format` already handles line length. However, this is a common pattern to avoid noisy warnings on strings/URLs that can't be wrapped. Acceptable.
- **Proposed additions** (not urgent):
  - `"RUF"` — Ruff-specific rules (catches Ruff-only patterns)
  - `"PTH"` — pathlib enforcement (already using pathlib everywhere, this would prevent regression)
  - `"PT"` — pytest-specific rules (would catch test anti-patterns)
  - `"TC"` — TYPE_CHECKING block enforcement
- `target-version = "py312"` is correct per `requires-python = ">=3.12"`.

## LangChain Adapter Compatibility — COMPATIBLE

- `GateModelAdapter` Protocol with `evaluate() -> GateDecision` is clean and compatible with LangChain structured output patterns.
- When a real LLM adapter is built, LangChain's `with_structured_output()` can return a dict that maps directly to `GateDecision` dataclass fields.
- The `ScaffoldGateModelAdapter` placeholder is well-structured for future replacement.
- No changes needed to the protocol to accommodate LangChain.

## Gradio API — VERIFIED

- `gr.Blocks()` with `gr.Code(language="python")` is the correct API for code editor components.
- `launch(share=False, quiet=True, prevent_thread_lock=True)` is the right pattern for embedded non-blocking launch.
- `app.close()` is the correct cleanup method.

## Path Handling — CORRECT

- All file operations use `pathlib.Path` consistently.
- No `os.path` usage found.
- All `write_text()` and `read_text()` calls specify `encoding="utf-8"`.

## General Code Quality

- No bare `except Exception: pass` in production Python (only in Gradio renderer with `contextlib.suppress`, which is the linter-recommended pattern).
- No secrets, tokens, or .env files in repo.
- Type hints used consistently.
