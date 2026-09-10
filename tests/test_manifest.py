"""Testes do manifesto do modelo promovido."""

from __future__ import annotations

from pathlib import Path

import pytest

from model_lifecycle.inspection_classes import CLASS_NAMES
from model_lifecycle.manifest import ModelManifest


def test_manifest_round_trip(tmp_path: Path) -> None:
    (tmp_path / "model.pt").write_bytes(b"model")
    manifest = ModelManifest(
        model_path="model.pt",
        format="pytorch",
        classes=CLASS_NAMES,
        confidence_threshold=0.75,
        image_size=224,
        dataset_hash="hash",
        ultralytics_version="8.2.0",
        metrics={"accuracy": 0.91},
    )
    path = tmp_path / "manifest.json"
    manifest.save(path)
    assert ModelManifest.load(path) == manifest


def test_manifest_rejects_wrong_classes() -> None:
    with pytest.raises(ValueError, match="classes oficiais"):
        ModelManifest(
            model_path="model.pt",
            format="pytorch",
            classes=("conforme",),
            confidence_threshold=0.75,
            image_size=224,
            dataset_hash="hash",
            ultralytics_version="8.2.0",
            metrics={},
        )
