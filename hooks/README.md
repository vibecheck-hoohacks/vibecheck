# Hooks

`hooks/` contains Claude-facing entrypoints and payload/response helpers.

- `pre_tool_use.py` is the blocking orchestration entrypoint for the `PreToolUse` hook.
- `stdin_payload.py` parses the hook payload from stdin and extracts tool metadata.
- `decision_output.py` emits the final `allow` or `deny` payload.

The scaffold keeps hook logic thin so normalization, gating, and QA remain testable in `core/` and `qa/`.
