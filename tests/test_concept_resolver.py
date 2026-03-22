"""Tests for core.concept_resolver — concept name resolution."""

from __future__ import annotations

from core.concept_resolver import ConceptResolution, normalize_concept_name, resolve_concept
from core.models import CompetenceEntry, CompetenceModel


def _model_with(*concept_names: str) -> CompetenceModel:
    return CompetenceModel(
        user_id="test",
        updated_at="2025-01-01T00:00:00Z",
        concepts={name: CompetenceEntry(score=0.5) for name in concept_names},
    )


class TestNormalizeConceptName:
    def test_lowercase(self) -> None:
        assert normalize_concept_name("Error Handling") == "error_handling"

    def test_special_chars(self) -> None:
        assert normalize_concept_name("async/await (Python)") == "async_await_python"

    def test_already_normalized(self) -> None:
        assert normalize_concept_name("data_structures") == "data_structures"

    def test_leading_trailing_junk(self) -> None:
        assert normalize_concept_name("  --hello-- ") == "hello"


class TestResolveConcept:
    def test_exact_match(self) -> None:
        model = _model_with("functions", "error_handling")
        result = resolve_concept("functions", model)
        assert result == ConceptResolution(action="existing", concept_name="functions")

    def test_normalized_match(self) -> None:
        model = _model_with("error_handling")
        result = resolve_concept("Error Handling", model)
        assert result.action == "existing"
        assert result.concept_name == "error_handling"
        assert result.mapped_from == "Error Handling"

    def test_creates_new_concept(self) -> None:
        model = _model_with("functions")
        result = resolve_concept("decorators", model)
        assert result.action == "created"
        assert result.concept_name == "decorators"
        assert "decorators" in model.concepts
        assert model.concepts["decorators"].score == 0.5
        assert model.concepts["decorators"].notes == ["Auto-created from gate classification"]

    def test_creates_normalized_name(self) -> None:
        model = _model_with("functions")
        result = resolve_concept("List Comprehensions", model)
        assert result.action == "created"
        assert result.concept_name == "list_comprehensions"
        assert result.mapped_from == "List Comprehensions"
