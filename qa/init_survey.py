"""Gradio-based competence model initialization survey.

Presents concept sliders for self-assessment, then writes the initial
competence model YAML.
"""

from __future__ import annotations

import contextlib
import importlib
import queue
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.competence_store import save_competence_model
from core.concept_taxonomy import ConceptDefinition, load_taxonomy
from core.models import CompetenceEntry, CompetenceEvidence, CompetenceModel

_TIMEOUT_SECONDS = 300  # 5 minutes

# Slider value (1-5) → initial competence score (0.0-1.0)
_SCORE_MAP: dict[int, float] = {1: 0.1, 2: 0.3, 3: 0.5, 4: 0.7, 5: 0.9}


def run_gradio_survey(
    output_path: Path,
    taxonomy: list[ConceptDefinition] | None = None,
) -> CompetenceModel | None:
    """Launch the Gradio survey and return the seeded model, or None on timeout."""
    try:
        gr = _import_gradio()
    except ImportError as exc:
        raise RuntimeError(
            "Gradio is not installed. Install with: uv pip install 'vibecheck[ui]'"
        ) from exc

    concepts = taxonomy or load_taxonomy()
    result_q: queue.Queue[dict[str, int]] = queue.Queue()

    app = _build_app(gr, concepts, result_q)
    server_thread = threading.Thread(target=_launch_app, args=(app,), daemon=True)
    server_thread.start()

    try:
        ratings = result_q.get(timeout=_TIMEOUT_SECONDS)
    except queue.Empty:
        _close_app(app)
        return None
    finally:
        _close_app(app)

    model = _build_model(concepts, ratings)
    save_competence_model(model, output_path)
    return model


def _build_app(
    gr: Any,
    concepts: list[ConceptDefinition],
    result_q: queue.Queue[dict[str, int]],
) -> Any:
    with gr.Blocks(title="VibeCheck Setup", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            "## VibeCheck — Competence Model Setup\n"
            "Rate your confidence with each concept below.\n"
            "**1** = No experience · **5** = Very confident"
        )

        sliders: list[Any] = []
        for concept in concepts:
            label = concept.name.replace("_", " ").title()
            s = gr.Slider(
                minimum=1,
                maximum=5,
                step=1,
                value=3,
                label=f"{label}  ({concept.category})",
            )
            sliders.append(s)

        submit_btn = gr.Button("Submit", variant="primary")
        status_text = gr.Markdown("")

        def on_submit(*slider_values: float) -> str:
            ratings = {concepts[i].name: int(v) for i, v in enumerate(slider_values)}
            result_q.put(ratings)
            return "Competence model saved. You can close this window."

        submit_btn.click(
            fn=on_submit,
            inputs=sliders,
            outputs=[status_text],
        )

    return app


def _build_model(
    concepts: list[ConceptDefinition],
    ratings: dict[str, int],
) -> CompetenceModel:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entries: dict[str, CompetenceEntry] = {}
    for concept in concepts:
        raw_rating = ratings.get(concept.name, 3)
        score = _SCORE_MAP.get(raw_rating, 0.5)
        entries[concept.name] = CompetenceEntry(
            score=score,
            notes=[],
            evidence=[
                CompetenceEvidence(
                    timestamp=now,
                    outcome="self_assessment",
                    note=f"User rated {raw_rating}/5",
                )
            ],
        )
    return CompetenceModel(user_id="local_default", updated_at=now, concepts=entries)


def _launch_app(app: Any) -> None:
    with contextlib.suppress(Exception):
        app.launch(share=False, quiet=True, prevent_thread_lock=True)


def _close_app(app: Any) -> None:
    with contextlib.suppress(Exception):
        app.close()


def _import_gradio() -> Any:
    return importlib.import_module("gradio")
