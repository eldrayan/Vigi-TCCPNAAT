"""Aquisição de sinais e imagens no nó de borda."""

from .camera import Camera, CameraFactory, load_opencv

__all__ = ["Camera", "CameraFactory", "load_opencv"]
