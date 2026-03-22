"""Tests for core.concept_taxonomy — taxonomy loading."""

from __future__ import annotations

from pathlib import Path

from core.concept_taxonomy import load_taxonomy


class TestLoadTaxonomy:
    def test_loads_default(self) -> None:
        concepts = load_taxonomy()
        assert len(concepts) >= 8
        names = [c.name for c in concepts]
        assert "variables_and_types" in names
        assert "functions" in names
        assert "async_programming" in names

    def test_prerequisites(self) -> None:
        concepts = load_taxonomy()
        by_name = {c.name: c for c in concepts}
        assert "variables_and_types" in by_name["functions"].prerequisites
        assert "functions" in by_name["error_handling"].prerequisites

    def test_loads_custom_file(self, tmp_path: Path) -> None:
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "concepts:\n"
            "  - name: widgets\n"
            "    category: custom\n"
            "  - name: gadgets\n"
            "    category: custom\n"
            "    prerequisites: [widgets]\n",
            encoding="utf-8",
        )
        concepts = load_taxonomy(custom)
        assert len(concepts) == 2
        assert concepts[1].prerequisites == ["widgets"]
