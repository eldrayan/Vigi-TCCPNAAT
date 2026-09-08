"""Contrato e fábrica dos backends de câmera."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any, Protocol

from edge.acquisition.backends import OpenCVCamera, Picamera2Camera
from edge.config import CollectionConfig


class Camera(Protocol):
    def is_opened(self) -> bool: ...

    def read(self) -> tuple[bool, Any]: ...

    def release(self) -> None: ...


def load_opencv() -> Any:
    """Carrega OpenCV somente no processo que usa aquisição de imagens."""
    try:
        return importlib.import_module("cv2")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenCV não encontrado. Instale com "
            "'sudo apt install python3-opencv' no Raspberry Pi OS."
        ) from exc


class CameraFactory:
    @staticmethod
    def resolve_backend(requested: str) -> str:
        if requested != "auto":
            return requested
        try:
            if importlib.util.find_spec("picamera2") is not None:
                return "picamera2"
        except (ImportError, AttributeError, ValueError):
            pass
        return "opencv"

    @staticmethod
    def create(config: CollectionConfig, cv2: Any, backend: str) -> Camera:
        if backend == "picamera2":
            camera: Camera = Picamera2Camera(
                device=config.camera,
                width=config.width,
                height=config.height,
                fps=config.fps,
                warmup_seconds=config.warmup_seconds,
            )
        else:
            camera = OpenCVCamera(
                cv2=cv2,
                device=config.camera,
                width=config.width,
                height=config.height,
                fps=config.fps,
            )

        if not camera.is_opened():
            camera.release()
            raise RuntimeError(
                f"Não foi possível abrir a câmera {config.camera} "
                f"com backend {backend}."
            )
        return camera
