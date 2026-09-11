"""Testes do manifesto do modelo promovido."""

from __future__ import annotations

from pathlib import Path

import pytest

from model_lifecycle.inspection_classes import CLASS_NAMES
from model_lifecycle.manifest import SUPPORTED_FORMATS, ModelManifest


def manifest_kwargs() -> dict[str, object]:
    return {
        "model_path": "model.pt",
        "format": "pytorch",
        "classes": CLASS_NAMES,
        "confidence_threshold": 0.75,
        "image_size": 224,
        "dataset_hash": "hash",
        "ultralytics_version": "8.2.0",
        "metrics": {
            "accuracy": 0.91,
            "false_negative_rate": 0.08,
            "false_positive_rate": 0.12,
        },
    }


def test_manifest_round_trip(tmp_path: Path) -> None:
    (tmp_path / "model.pt").write_bytes(b"model")
    manifest = ModelManifest(**manifest_kwargs())
    path = tmp_path / "manifest.json"
    manifest.save(path)
    assert ModelManifest.load(path) == manifest


def test_manifest_rejects_wrong_classes() -> None:
    kwargs = manifest_kwargs()
    kwargs["classes"] = ("conforme",)
    with pytest.raises(ValueError, match="classes oficiais"):
        ModelManifest(**kwargs)


def test_manifest_supports_only_pytorch() -> None:
    assert SUPPORTED_FORMATS == {"pytorch"}
    kwargs = manifest_kwargs()
    kwargs["format"] = "tflite"
    kwargs["model_path"] = "model.tflite"
    with pytest.raises(ValueError, match="Formato nao suportado"):
        ModelManifest(**kwargs)


@pytest.mark.parametrize("model_path", ["model.tflite", "model.onnx", "model"])
def test_manifest_requires_pt_extension(model_path: str) -> None:
    kwargs = manifest_kwargs()
    kwargs["model_path"] = model_path
    with pytest.raises(ValueError, match="extensao .pt"):
        ModelManifest(**kwargs)


@pytest.mark.parametrize("model_path", ["/tmp/model.pt", "../model.pt"])
def test_manifest_rejects_model_outside_its_directory(model_path: str) -> None:
    kwargs = manifest_kwargs()
    kwargs["model_path"] = model_path
    with pytest.raises(ValueError, match="diretorio do manifesto"):
        ModelManifest(**kwargs)


@pytest.mark.parametrize("value", [True, "0.75", float("nan"), float("inf"), -0.1, 1.1])
def test_manifest_rejects_invalid_threshold(value: object) -> None:
    kwargs = manifest_kwargs()
    kwargs["confidence_threshold"] = value
    with pytest.raises(ValueError, match="confidence_threshold"):
        ModelManifest(**kwargs)


@pytest.mark.parametrize("value", [True, 0, -1, 224.0])
def test_manifest_rejects_invalid_image_size(value: object) -> None:
    kwargs = manifest_kwargs()
    kwargs["image_size"] = value
    with pytest.raises(ValueError, match="image_size"):
        ModelManifest(**kwargs)
