"""Resolve concept names to existing competence model entries.

MVP scope: exact match + string normalization only.
LLM-assisted fuzzy matching is deferred to the graph competence spec.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from core.models import CompetenceEntry, CompetenceModel


@dataclass(slots=True)
class ConceptResolution:
    action: Literal["existing", "created"]
    concept_name: str
    mapped_from: str | None = None


def normalize_concept_name(raw: str) -> str:
    """Normalize a concept name to lowercase snake_case."""
    name = raw.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def resolve_concept(name: str, model: CompetenceModel) -> ConceptResolution:
    """Resolve a concept name against the model, creating a new entry if needed."""
    # Exact match
    if name in model.concepts:
        return ConceptResolution(action="existing", concept_name=name)

    # Normalized match
    normalized = normalize_concept_name(name)
    if normalized in model.concepts:
        return ConceptResolution(action="existing", concept_name=normalized, mapped_from=name)

    # Check if any existing concept normalizes to the same thing
    for existing_name in model.concepts:
        if normalize_concept_name(existing_name) == normalized:
            return ConceptResolution(
                action="existing", concept_name=existing_name, mapped_from=name
            )

    # Create new concept node
    model.concepts[normalized] = CompetenceEntry(
        score=0.5,
        notes=["Auto-created from gate classification"],
        evidence=[],
    )
    return ConceptResolution(
        action="created",
        concept_name=normalized,
        mapped_from=name if name != normalized else None,
    )
