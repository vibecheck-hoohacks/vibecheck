from __future__ import annotations

from core.competence_store import update_competence_entry
from core.models import CompetenceModel


def apply_qa_outcome(
    competence_model: CompetenceModel,
    *,
    concepts: list[str],
    passed: bool,
    attempt_count: int,
) -> CompetenceModel:
    target_concepts = concepts or ["general_programming"]
    if passed:
        delta = 0.08 if attempt_count == 1 else 0.04
        outcome = "pass_first_try" if attempt_count == 1 else f"pass_after_{attempt_count}"
        note = "Validated understanding through scaffold QA."
    else:
        delta = -0.06
        outcome = "fail_limit_reached"
        note = "Reached QA fail limit; potential epistemic debt remains."

    for concept in target_concepts:
        update_competence_entry(
            competence_model,
            concept=concept,
            delta=delta,
            note=note,
            outcome=outcome,
        )
    return competence_model
