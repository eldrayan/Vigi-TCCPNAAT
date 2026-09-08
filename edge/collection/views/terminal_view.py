"""Interface interativa para coleta em sessões SSH sem display gráfico."""

from __future__ import annotations

import select
import sys
import termios
import tty
from typing import Any

from edge.collection.state import CaptureState


class TerminalCollectionView:
    headless = True

    def __init__(self) -> None:
        self.file_descriptor: int | None = None
        self.previous_settings: list[Any] | None = None

    def open(self) -> None:
        if not sys.stdin.isatty():
            raise RuntimeError(
                "O modo sem janela precisa de um terminal interativo para receber "
                "as teclas. Execute o comando diretamente no terminal/SSH."
            )
        self.file_descriptor = sys.stdin.fileno()
        self.previous_settings = termios.tcgetattr(self.file_descriptor)
        tty.setcbreak(self.file_descriptor)
        print(
            "[INFO] Sessão gráfica não detectada: modo terminal ativado. "
            "Os controles continuam iguais, mas não haverá visualização da mira."
        )

    def read_key(self) -> int:
        if self.file_descriptor is None:
            return -1
        readable, _, _ = select.select([sys.stdin], [], [], 0)
        if not readable:
            return -1
        character = sys.stdin.read(1)
        return ord(character) if character else -1

    def render(
        self,
        frame: Any,
        state: CaptureState,
        guide: tuple[int, int, int, int],
        score: float,
        threshold: float,
        message: str,
    ) -> None:
        return None

    def notify(self, category: str, message: str) -> None:
        print(f"\n[{category}] {message}")

    def close(self) -> None:
        if self.file_descriptor is not None and self.previous_settings is not None:
            termios.tcsetattr(
                self.file_descriptor, termios.TCSADRAIN, self.previous_settings
            )
        self.file_descriptor = None
        self.previous_settings = None
