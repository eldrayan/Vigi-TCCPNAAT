"""Interfaces disponíveis para operar o coletor."""

from .base import CollectionView
from .factory import create_view, graphical_display_available

__all__ = ["CollectionView", "create_view", "graphical_display_available"]
