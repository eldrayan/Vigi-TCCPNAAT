"""
Descrição: Armazena as imagens produzidas pelos ciclos de inspeção.
Autor: Leôncio Ferreira
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class InspectionCaptureStore:
    def __init__(self, directory: Path, cv2: Any | None = None) -> None:
        if cv2 is None:
            import cv2 as opencv

            cv2 = opencv
        self.directory = directory
        self.cv2 = cv2

    def save(self, frame: Any, *, inspection_id: int, result: str) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        image = (
            self.cv2.cvtColor(frame, self.cv2.COLOR_RGB2BGR)
            if frame.ndim == 3 and frame.shape[2] == 3
            else frame
        )
        self.cv2.imwrite(str(self.directory / "ultima_inspecao.jpg"), image)
        self.cv2.imwrite(
            str(self.directory / f"inspecao_{inspection_id}_{result}.jpg"), image
        )
