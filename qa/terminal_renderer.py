from __future__ import annotations

import sys
from pathlib import Path

from core.models import QAPacket


class TerminalQARenderer:
    def ask(self, question: str, attempt_number: int, packet: QAPacket) -> str:
        del packet
        prompt = f"\n[VibeCheck attempt {attempt_number}]\n{question}\n\n> "
        tty_path = Path("/dev/tty")
        if tty_path.exists():
            with tty_path.open("r+", encoding="utf-8") as tty:
                tty.write(prompt)
                tty.flush()
                return tty.readline().strip()

        print(prompt, file=sys.stderr, end="")
        return input().strip()
