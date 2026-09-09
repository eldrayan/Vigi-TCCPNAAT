"""Implementações concretas de aquisição por câmera."""

from .opencv_camera import OpenCVCamera
from .picamera2_camera import Picamera2Camera

__all__ = ["OpenCVCamera", "Picamera2Camera"]
