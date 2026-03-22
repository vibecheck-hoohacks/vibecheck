from __future__ import annotations

from core.llm_adapter import GateModelAdapter, ScaffoldGateModelAdapter
from core.models import AggregatedContext, ChangeProposal, CompetenceModel, GateDecision


class KnowledgeGate:
    def __init__(self, adapter: GateModelAdapter | None = None) -> None:
        self.adapter = adapter or ScaffoldGateModelAdapter()

    def evaluate(
        self,
        proposal: ChangeProposal,
        aggregated_context: AggregatedContext,
        competence_model: CompetenceModel,
    ) -> GateDecision:
        return self.adapter.evaluate(proposal, aggregated_context, competence_model)


def evaluate_change(
    proposal: ChangeProposal,
    aggregated_context: AggregatedContext,
    competence_model: CompetenceModel,
) -> GateDecision:
    return KnowledgeGate().evaluate(proposal, aggregated_context, competence_model)
