from core.competence_store import default_competence_model
from core.models import (
    ChangeProposal,
    ChangeTarget,
    CompetenceGap,
    DiffStats,
    GateDecision,
    QAPacket,
)
from qa.evaluation import AnswerEvaluation
from qa.llm_wrapper import GeneratedQuestion
from qa.loop import QALoop


class FakeRenderer:
    def __init__(self, answers: list[str]) -> None:
        self.answers = answers
        self.index = 0

    def ask(self, question: str, attempt_number: int, packet: QAPacket) -> str:
        del question, attempt_number, packet
        answer = self.answers[self.index]
        self.index += 1
        return answer


class FakeLLMClient:
    def __init__(self, evaluations: list[AnswerEvaluation]) -> None:
        self._evaluations = evaluations
        self._eval_index = 0
        self._question_count = 0

    def generate_question(self, gate_decision, attempt_number, competence_entries=None):
        self._question_count += 1
        return GeneratedQuestion(
            question=f"Generated question for attempt {attempt_number}",
            distractors=["Wrong answer 1", "Wrong answer 2"],
            hint="Think about the mechanism.",
        )

    def evaluate_answer(self, question, answer, question_type, context_excerpt, attempt_number):
        evaluation = self._evaluations[self._eval_index]
        self._eval_index += 1
        return evaluation


def test_qa_loop_passes_after_retry(tmp_path, monkeypatch) -> None:
    from qa import llm_wrapper as llm_wrapper_module

    fake_evaluations = [
        AnswerEvaluation(passed=False, feedback="Try again with more detail."),
        AnswerEvaluation(passed=True, feedback="Good explanation!"),
    ]
    fake_client = FakeLLMClient(fake_evaluations)
    llm_wrapper_module._client = fake_client

    proposal = ChangeProposal(
        proposal_id="proposal-1",
        session_id="session-1",
        tool_use_id="tool-1",
        tool_name="Write",
        cwd="/repo",
        targets=[
            ChangeTarget(
                path="core/example.py",
                language="python",
                old_content="",
                new_content="value = 1\n",
            )
        ],
        unified_diff="+value = 1",
        diff_stats=DiffStats(files_changed=1, additions=1, deletions=0),
        created_at="2026-03-21T00:00:00Z",
    )
    gate_decision = GateDecision(
        decision="block",
        reasoning="Need a quick explanation.",
        confidence=0.5,
        relevant_concepts=["python_basics"],
        competence_gap=CompetenceGap(size="medium", rationale="Scaffold test."),
        qa_packet=QAPacket(
            question_type="plain_english",
            prompt_seed="Explain why the assignment is safe.",
            context_excerpt="+value = 1",
        ),
    )
    competence_model = default_competence_model()
    competence_path = tmp_path / "state" / "competence_model.yaml"
    loop = QALoop(
        renderer=FakeRenderer(
            ["too short", "This change assigns a constant value and does not alter control flow."]
        )
    )

    result = loop.run(
        proposal=proposal,
        gate_decision=gate_decision,
        competence_model=competence_model,
        competence_path=competence_path,
        state_dir=tmp_path / "state",
    )

    assert result.final_decision == "allow"
    assert result.passed is True
    assert result.attempt_count == 2
    assert (tmp_path / "state" / "qa" / "results" / "proposal-1.yaml").exists()
    saved_competence = competence_path.read_text(encoding="utf-8")
    assert "pass_after_2" in saved_competence
