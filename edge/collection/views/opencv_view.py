"""Interface gráfica do coletor baseada no OpenCV."""

from __future__ import annotations

import time
from typing import Any

from edge.collection.state import CaptureState


class OpenCVCollectionView:
    window_name = "Vigi - Coleta Assistida"
    headless = False

    def __init__(self, cv2: Any) -> None:
        self.cv2 = cv2
        self.message = "Posicione a garrafa dentro da guia"
        self.message_until = time.monotonic() + 3

    def open(self) -> None:
        self.cv2.namedWindow(self.window_name, self.cv2.WINDOW_NORMAL)

    def read_key(self) -> int:
        return self.cv2.waitKey(1) & 0xFF

    def render(
        self,
        frame: Any,
        state: CaptureState,
        guide: tuple[int, int, int, int],
        score: float,
        threshold: float,
        message: str,
    ) -> None:
        if message:
            self.message = message
            self.message_until = time.monotonic() + 1.5
        visible_message = self.message if time.monotonic() < self.message_until else ""
        preview = self._draw_overlay(
            frame, state, guide, score, threshold, visible_message
        )
        self.cv2.imshow(self.window_name, preview)

    def notify(self, category: str, message: str) -> None:
        self.message = message
        self.message_until = time.monotonic() + 2

    def close(self) -> None:
        self.cv2.destroyAllWindows()

    def _draw_overlay(
        self,
        frame: Any,
        state: CaptureState,
        guide: tuple[int, int, int, int],
        score: float,
        threshold: float,
        message: str,
    ) -> Any:
        preview = frame.copy()
        x1, y1, x2, y2 = guide
        color = (0, 220, 0) if score >= threshold or threshold <= 0 else (0, 80, 255)
        self.cv2.rectangle(preview, (x1, y1), (x2, y2), color, 2)
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        self.cv2.line(
            preview, (center_x - 18, center_y), (center_x + 18, center_y), color, 1
        )
        self.cv2.line(
            preview, (center_x, center_y - 18), (center_x, center_y + 18), color, 1
        )

        mode = "BURST ATIVO" if state.burst_enabled else "MANUAL"
        crop = "ROI" if state.crop_guide else "QUADRO INTEIRO"
        lines = [
            f"Classe [{state.selected_class}]: {state.class_name}",
            f"Frasco fisico: {state.physical_sample:03d} | {mode} | {crop}",
            (
                f"Nitidez: {score:.1f} | Salvas nesta classe: "
                f"{state.saved_by_class[state.selected_class]}"
            ),
            (
                "1-4 classe | ESPACO foto | B burst | N proximo frasco | "
                "C recorte | Q sair"
            ),
        ]
        overlay_height = 28 * len(lines) + (30 if message else 0)
        self.cv2.rectangle(
            preview, (0, 0), (preview.shape[1], overlay_height), (0, 0, 0), -1
        )
        for index, line in enumerate(lines):
            self.cv2.putText(
                preview,
                line,
                (12, 24 + index * 28),
                self.cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                1,
                self.cv2.LINE_AA,
            )
        if message:
            self.cv2.putText(
                preview,
                message,
                (12, 24 + len(lines) * 28),
                self.cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2,
                self.cv2.LINE_AA,
            )
        return preview
