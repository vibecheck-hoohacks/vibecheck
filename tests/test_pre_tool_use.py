from hooks.pre_tool_use import handle_pre_tool_use


def test_pre_tool_use_allows_small_change_without_qa(tmp_path) -> None:
    response = handle_pre_tool_use(
        {
            "tool_name": "Write",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "cwd": "/repo",
            "user_prompt_excerpt": "Rename a variable.",
            "input": {
                "path": "core/example.py",
                "old_content": "value = 1\n",
                "new_content": "value = 2\n",
            },
        },
        state_dir=tmp_path / "state",
    )

    assert response["decision"] == "allow"
    assert (tmp_path / "state" / "agg" / "current_attempt.md").exists()
    assert (tmp_path / "state" / "competence_model.yaml").exists()
