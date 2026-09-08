"""Seleção da interface gráfica ou terminal."""

from __future__ import annotations

import os
from typing import Any

from edge.collection.views.base import CollectionView
from edge.collection.views.opencv_view import OpenCVCollectionView
from edge.collection.views.terminal_view import TerminalCollectionView


def graphical_display_available(environment: dict[str, str] | None = None) -> bool:
    environment = os.environ if environment is None else environment
    return bool(environment.get("DISPLAY") or environment.get("WAYLAND_DISPLAY"))


def create_view(cv2: Any, force_headless: bool) -> CollectionView:
    if force_headless or not graphical_display_available():
        return TerminalCollectionView()
    return OpenCVCollectionView(cv2)
