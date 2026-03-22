# VibeCheck

VibeCheck is a Python-first scaffold for a competence-aware guardrail in the Claude Code mutation path.

## Architecture

The initial project shape follows the MVP spec directly:

- `hooks/` holds Claude-facing hook entrypoints and decision output helpers.
- `core/` holds mutation normalization, context aggregation, gate orchestration, and competence state logic.
- `qa/` holds the blocking QA loop plus terminal and optional Gradio renderer boundaries.
- `state/` holds inspectable persisted artifacts like YAML, Markdown, and JSONL files.
- `tests/` covers the scaffold seams so the structure stays stable as implementation fills in.

## Tooling

This repo uses `uv` for Python environment and dependency management.

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Notes

- The current gate adapter is a deterministic scaffold, not the final model-backed evaluator.
- Terminal QA is the day-one path.
- `qa/gradio_renderer.py` is the optional Python web UI seam if richer browser-based QA becomes necessary.
