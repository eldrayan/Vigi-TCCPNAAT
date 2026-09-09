"""Adaptador de captura direta para câmeras CSI via Picamera2."""

from __future__ import annotations

import importlib
import time
from typing import Any


class Picamera2Camera:
    def __init__(
        self,
        device: int,
        width: int,
        height: int,
        fps: int,
        warmup_seconds: float,
    ) -> None:
        try:
            picamera2_module = importlib.import_module("picamera2")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Picamera2 não foi encontrado. No Raspberry Pi OS, instale "
                "com 'sudo apt install python3-picamera2'."
            ) from exc

        self.camera = picamera2_module.Picamera2(camera_num=device)
        self.started = False
        try:
            configuration = self.camera.create_video_configuration(
                main={"size": (width, height), "format": "BGR888"},
                controls={"FrameRate": float(fps)},
                buffer_count=4,
            )
            self.camera.configure(configuration)
            self.camera.start()
            self.started = True
            self._enable_continuous_autofocus_when_available()
        except Exception as exc:
            self.camera.close()
            raise RuntimeError(
                f"Não foi possível inicializar a câmera CSI {device} via Picamera2."
            ) from exc

        if warmup_seconds > 0:
            time.sleep(warmup_seconds)

    def _enable_continuous_autofocus_when_available(self) -> None:
        if "AfMode" not in self.camera.camera_controls:
            return
        libcamera = importlib.import_module("libcamera")
        self.camera.set_controls({"AfMode": libcamera.controls.AfModeEnum.Continuous})

    def is_opened(self) -> bool:
        return self.started

    def read(self) -> tuple[bool, Any]:
        frame = self.camera.capture_array("main")
        return frame is not None, frame

    def release(self) -> None:
        if self.started:
            self.camera.stop()
            self.camera.close()
            self.started = False
