from core.competence_store import default_competence_model
from core.context_aggregation import build_aggregated_context
from core.gate import evaluate_change
from core.normalize import normalize_mutation_payload


def test_gate_allows_small_change(tmp_path) -> None:
    proposal = normalize_mutation_payload(
        {
            "tool_name": "Write",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "cwd": "/repo",
            "input": {
                "path": "core/example.py",
                "old_content": "x = 1\n",
                "new_content": "x = 2\n",
            },
        }
    )
    aggregated = build_aggregated_context(proposal, tmp_path)

    decision = evaluate_change(proposal, aggregated, default_competence_model())

    assert decision.decision == "allow"
    assert decision.qa_packet is None


def test_gate_blocks_larger_change(tmp_path) -> None:
    big_new_content = "\n".join(f"line_{index} = {index}" for index in range(30))
    proposal = normalize_mutation_payload(
        {
            "tool_name": "Write",
            "session_id": "session-1",
            "tool_use_id": "tool-1",
            "cwd": "/repo",
            "input": {
                "path": "core/example.py",
                "old_content": "",
                "new_content": big_new_content,
            },
        }
    )
    aggregated = build_aggregated_context(proposal, tmp_path)

    decision = evaluate_change(proposal, aggregated, default_competence_model())

    assert decision.decision == "block"
    assert decision.qa_packet is not None
    assert decision.qa_packet.question_type == "plain_english"
