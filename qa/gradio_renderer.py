from __future__ import annotations

import importlib.util

from core.models import QAPacket


def gradio_available() -> bool:
    return importlib.util.find_spec("gradio") is not None


class GradioQARenderer:
    def ask(self, question: str, attempt_number: int, packet: QAPacket) -> str:
        del question, attempt_number, packet
        raise NotImplementedError(
            "Gradio-backed blocking QA is reserved for a later implementation pass. "
            "Add Gradio with uv and wire a local completion mechanism before selecting this renderer."
        )
