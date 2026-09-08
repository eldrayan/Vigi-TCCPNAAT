"""Adaptador para webcams USB expostas pelo OpenCV."""

from __future__ import annotations

from typing import Any


class OpenCVCamera:
    def __init__(
        self, cv2: Any, device: int, width: int, height: int, fps: int
    ) -> None:
        self.capture = cv2.VideoCapture(device)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, fps)

    def is_opened(self) -> bool:
        return bool(self.capture.isOpened())

    def read(self) -> tuple[bool, Any]:
        return self.capture.read()

    def release(self) -> None:
        self.capture.release()
