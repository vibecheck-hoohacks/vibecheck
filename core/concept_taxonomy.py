"""Load and parse the default concept taxonomy from YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

_DEFAULT_TAXONOMY_PATH = (
    Path(__file__).resolve().parents[1] / "state" / "default_concept_graph.yaml"
)


@dataclass(slots=True)
class ConceptDefinition:
    name: str
    category: str
    prerequisites: list[str] = field(default_factory=list)


def load_taxonomy(path: Path | None = None) -> list[ConceptDefinition]:
    """Load the concept taxonomy from YAML, returning ordered concept definitions."""
    p = path or _DEFAULT_TAXONOMY_PATH
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    concepts: list[ConceptDefinition] = []
    for entry in raw.get("concepts", []):
        concepts.append(
            ConceptDefinition(
                name=str(entry["name"]),
                category=str(entry.get("category", "general")),
                prerequisites=[str(p) for p in entry.get("prerequisites", [])],
            )
        )
    return concepts
