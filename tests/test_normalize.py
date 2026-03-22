from core.normalize import is_code_mutation_tool, normalize_mutation_payload


def test_normalize_single_write_payload() -> None:
    payload = {
        "tool_name": "Write",
        "session_id": "session-1",
        "tool_use_id": "tool-1",
        "cwd": "/repo",
        "input": {
            "path": "core/example.py",
            "old_content": "print('old')\n",
            "new_content": "print('new')\n",
        },
    }

    proposal = normalize_mutation_payload(payload)

    assert proposal.tool_name == "Write"
    assert proposal.targets[0].language == "python"
    assert proposal.diff_stats.files_changed == 1
    assert proposal.diff_stats.additions == 1
    assert proposal.diff_stats.deletions == 1
    assert "+print('new')" in proposal.unified_diff


def test_is_code_mutation_tool_recognizes_supported_tools() -> None:
    assert is_code_mutation_tool("Write") is True
    assert is_code_mutation_tool("Edit") is True
    assert is_code_mutation_tool("Bash") is False
