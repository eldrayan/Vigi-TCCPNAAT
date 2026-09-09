"""Contrato de apresentação do coletor."""

from __future__ import annotations

from typing import Any, Protocol

from edge.collection.state import CaptureState


class CollectionView(Protocol):
    @property
    def headless(self) -> bool: ...

    def open(self) -> None: ...

    def read_key(self) -> int: ...

    def render(
        self,
        frame: Any,
        state: CaptureState,
        guide: tuple[int, int, int, int],
        score: float,
        threshold: float,
        message: str,
    ) -> None: ...

    def notify(self, category: str, message: str) -> None: ...

    def close(self) -> None: ...
