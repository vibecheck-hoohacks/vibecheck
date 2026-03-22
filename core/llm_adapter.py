from __future__ import annotations

from typing import Protocol

from core.models import (
    AggregatedContext,
    ChangeProposal,
    CompetenceGap,
    CompetenceModel,
    GateDecision,
    QAPacket,
    RelevantCompetenceEntry,
)


class GateModelAdapter(Protocol):
    def evaluate(
        self,
        proposal: ChangeProposal,
        aggregated_context: AggregatedContext,
        competence_model: CompetenceModel,
    ) -> GateDecision: ...


class ScaffoldGateModelAdapter:
    """Deterministic placeholder until a real evaluator model is wired in."""

    def evaluate(
        self,
        proposal: ChangeProposal,
        aggregated_context: AggregatedContext,
        competence_model: CompetenceModel,
    ) -> GateDecision:
        del aggregated_context

        change_size = proposal.diff_stats.additions + proposal.diff_stats.deletions
        relevant_concepts = _guess_relevant_concepts(proposal)
        relevant_entries = _relevant_entries(competence_model, relevant_concepts)

        if proposal.diff_stats.files_changed == 1 and change_size <= 5:
            return GateDecision(
                decision="allow",
                reasoning="Scaffold gate allows very small single-file changes by default.",
                confidence=0.78,
                relevant_concepts=relevant_concepts,
                relevant_competence_entries=relevant_entries,
            )

        gap_size = "high" if change_size > 40 else "medium"
        question_type = "faded_example" if gap_size == "high" else "plain_english"
        return GateDecision(
            decision="block",
            reasoning="Scaffold gate requests a knowledge check for larger or multi-file changes.",
            confidence=0.56,
            relevant_concepts=relevant_concepts,
            relevant_competence_entries=relevant_entries,
            competence_gap=CompetenceGap(
                size=gap_size,
                rationale="The placeholder evaluator uses diff size as a conservative proxy for complexity.",
            ),
            qa_packet=QAPacket(
                question_type=question_type,
                prompt_seed="Explain why the proposed change works and what could break.",
                context_excerpt=proposal.unified_diff[:800],
            ),
        )


def _guess_relevant_concepts(proposal: ChangeProposal) -> list[str]:
    languages = {target.language for target in proposal.targets if target.language}
    if "python" in languages:
        return ["python_basics"]
    if languages:
        return [f"{language}_basics" for language in sorted(languages)]
    return ["general_programming"]


def _relevant_entries(
    competence_model: CompetenceModel,
    concepts: list[str],
) -> list[RelevantCompetenceEntry]:
    entries: list[RelevantCompetenceEntry] = []
    for concept in concepts:
        entry = competence_model.concepts.get(concept)
        if entry is None:
            continue
        entries.append(
            RelevantCompetenceEntry(
                concept=concept,
                score=entry.score,
                notes=list(entry.notes),
            )
        )
    return entries
