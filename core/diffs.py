from __future__ import annotations

from difflib import unified_diff
from pathlib import Path

from core.models import DiffStats

LANGUAGE_BY_SUFFIX = {
    ".css": "css",
    ".html": "html",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript",
    ".md": "markdown",
    ".py": "python",
    ".rs": "rust",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".yaml": "yaml",
    ".yml": "yaml",
}


def detect_language(path: str) -> str | None:
    return LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower())


def build_unified_diff(old_content: str | None, new_content: str, path: str) -> str:
    old_lines = [] if old_content is None else old_content.splitlines()
    new_lines = new_content.splitlines()
    return "\n".join(
        unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}", lineterm="")
    )


def count_diff_stats(unified_diff_text: str, files_changed: int) -> DiffStats:
    additions = 0
    deletions = 0
    for line in unified_diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            additions += 1
        elif line.startswith("-"):
            deletions += 1
    return DiffStats(files_changed=files_changed, additions=additions, deletions=deletions)
