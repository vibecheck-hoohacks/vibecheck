from __future__ import annotations

from core.models import GateDecision, QuestionType


def select_question_type(gap_size: str) -> QuestionType:
    if gap_size == "high":
        return "faded_example"
    if gap_size == "low":
        return "true_false"
    return "plain_english"


def build_question_prompt(gate_decision: GateDecision, attempt_number: int) -> str:
    qa_packet = gate_decision.qa_packet
    if qa_packet is None:
        raise ValueError("Cannot build a question without a QA packet.")

    intro = {
        1: "Explain the mechanism behind this change.",
        2: "Try again with more concrete reasoning about execution flow.",
        3: "Final attempt: answer with the clearest mechanism-focused explanation you can.",
    }.get(attempt_number, "Explain the mechanism behind this change.")

    return "\n\n".join(
        [
            intro,
            f"Question type: {qa_packet.question_type}",
            f"Seed: {qa_packet.prompt_seed}",
            "Context excerpt:",
            qa_packet.context_excerpt or "<missing>",
        ]
    )


def build_follow_up_question(question: str, feedback: str) -> str:
    return f"{question}\n\nGuidance: {feedback}"
