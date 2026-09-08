"""Métricas simples de qualidade da imagem coletada."""

from __future__ import annotations

from typing import Any


def sharpness_score(cv2: Any, frame: Any) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())
