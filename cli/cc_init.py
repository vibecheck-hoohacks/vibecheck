"""``vibecheck cc init`` — bootstrap Claude Code hook configuration."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

from core.competence_store import default_competence_model, save_competence_model

_STATE_SUBDIRS = ["logs", "qa/pending", "qa/results", "agg"]


def run_cc_init(*, target_dir: str | None = None) -> None:
    source_root = Path(__file__).resolve().parents[1]
    project_root = (Path(target_dir).resolve() if target_dir else Path.cwd())
    claude_dir = project_root / ".claude"
    settings_path = claude_dir / "settings.json"
    state_dir = project_root / "state"
    hook_config = _build_hook_config(source_root)

    # 1. Create/merge .claude/settings.json
    claude_dir.mkdir(exist_ok=True)
    settings = _load_or_empty(settings_path)
    _merge_hook(settings, hook_config)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print(f"  Wrote hook config to {settings_path}")

    # 2. Create state directory structure
    state_dir.mkdir(exist_ok=True)
    for subdir in _STATE_SUBDIRS:
        (state_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(f"  Created state directories under {state_dir}/")

    # 3. Create default competence model if missing
    cm_path = state_dir / "competence_model.yaml"
    if not cm_path.exists():
        model = default_competence_model()
        save_competence_model(model, cm_path)
        print(f"  Created default competence model at {cm_path}")
    else:
        print(f"  Competence model already exists at {cm_path}")

    print("\nVibeCheck is ready. Claude Code will use the PreToolUse hook")
    print(
        "to gate Edit, Write, and MultiEdit calls via: "
        f"{hook_config['hooks'][0]['command']}"
    )


def _load_or_empty(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def _build_hook_config(source_root: Path) -> dict[str, Any]:
    python_executable = shlex.quote(sys.executable)
    root = shlex.quote(str(source_root))
    hook_script = shlex.quote(str(source_root / "hooks" / "pre_tool_use.py"))
    hook_command = f"sh -lc 'cd {root} && {python_executable} {hook_script}'"

    return {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
            {
                "type": "command",
                "command": hook_command,
                "timeout": 30,
            }
        ],
    }


def _merge_hook(settings: dict, hook_config: dict[str, Any]) -> None:
    """Add the VibeCheck PreToolUse hook without clobbering existing hooks."""
    hooks = settings.setdefault("hooks", {})
    pre_tool_use: list = hooks.setdefault("PreToolUse", [])

    # Check if a vibecheck hook already exists
    for entry in pre_tool_use:
        entry_hooks = entry.get("hooks", [])
        for h in entry_hooks:
            command = h.get("command", "")
            if "hooks.pre_tool_use" in command or "pre_tool_use.py" in command:
                return  # Already configured

    pre_tool_use.append(hook_config)
