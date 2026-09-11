"""Testes da promocao transacional do modelo."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from PIL import Image

from model_lifecycle.inspection_classes import CLASS_NAMES
from model_lifecycle.manifest import ModelManifest
from scripts import promover_modelo


def build_dataset(root: Path) -> None:
    for split_index, split in enumerate(("train", "val", "test")):
        for class_index, class_name in enumerate(CLASS_NAMES):
            directory = root / split / class_name
            directory.mkdir(parents=True)
            Image.new(
                "RGB",
                (8, 8),
                color=(split_index * 50, class_index * 40, 10),
            ).save(directory / f"{split}-{class_name}.png")


def write_metrics(path: Path, **changes: object) -> None:
    payload: dict[str, object] = {
        "accuracy": 0.91,
        "false_negative_rate": 0.08,
        "false_positive_rate": 0.12,
        "quality_gate": {
            "approved": True,
            "confidence_threshold": 0.72,
        },
    }
    payload.update(changes)
    path.write_text(json.dumps(payload), encoding="utf-8")


def inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    model = tmp_path / "candidate.pt"
    model.write_bytes(b"new-model")
    metrics = tmp_path / "metrics.json"
    write_metrics(metrics)
    dataset = tmp_path / "dataset"
    build_dataset(dataset)
    output = tmp_path / "active"
    return model, metrics, dataset, output


def seed_active(output: Path) -> None:
    output.mkdir()
    (output / "vigi-yolov8n-cls.pt").write_bytes(b"old-model")
    (output / "manifest.json").write_text("old-manifest", encoding="utf-8")


def assert_active_unchanged(output: Path) -> None:
    assert (output / "vigi-yolov8n-cls.pt").read_bytes() == b"old-model"
    assert (output / "manifest.json").read_text(encoding="utf-8") == "old-manifest"


def test_promotes_pt_with_threshold_from_report(tmp_path: Path) -> None:
    model, metrics, dataset, output = inputs(tmp_path)

    target, manifest_path = promover_modelo.promote_model(
        model, metrics, dataset, 224, output
    )

    assert target.read_bytes() == b"new-model"
    manifest = ModelManifest.load(manifest_path)
    assert manifest.format == "pytorch"
    assert manifest.model_path == "vigi-yolov8n-cls.pt"
    assert manifest.confidence_threshold == 0.72


@pytest.mark.parametrize("legacy_option", ["--threshold", "--format"])
def test_cli_rejects_legacy_options(legacy_option: str) -> None:
    with pytest.raises(SystemExit) as exc_info:
        promover_modelo.main([legacy_option, "value"])
    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("accuracy", True),
        ("accuracy", "0.91"),
        ("accuracy", float("nan")),
        ("accuracy", float("inf")),
        ("accuracy", -0.1),
        ("accuracy", 1.1),
        ("accuracy", 0.89),
        ("false_negative_rate", 0.11),
        ("false_positive_rate", 0.16),
    ],
)
def test_invalid_metric_preserves_active(
    tmp_path: Path, field: str, value: object
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    write_metrics(metrics, **{field: value})
    seed_active(output)

    with pytest.raises(ValueError):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)

    assert_active_unchanged(output)


@pytest.mark.parametrize("value", [True, "0.72", float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_report_threshold_preserves_active(
    tmp_path: Path, value: object
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    write_metrics(
        metrics,
        quality_gate={"approved": True, "confidence_threshold": value},
    )
    seed_active(output)

    with pytest.raises(ValueError, match="confidence_threshold"):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)

    assert_active_unchanged(output)


@pytest.mark.parametrize("image_size", [0, -1, True])
def test_invalid_image_size_preserves_active(
    tmp_path: Path, image_size: object
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    seed_active(output)

    with pytest.raises(ValueError, match="imgsz"):
        promover_modelo.promote_model(  # type: ignore[arg-type]
            model, metrics, dataset, image_size, output
        )

    assert_active_unchanged(output)


def test_tflite_candidate_is_rejected(tmp_path: Path) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    tflite = model.with_suffix(".tflite")
    model.rename(tflite)
    with pytest.raises(ValueError, match="PyTorch .pt"):
        promover_modelo.promote_model(tflite, metrics, dataset, 224, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "payload",
    [
        "not-json",
        "[]",
        json.dumps({"accuracy": 0.91}),
        json.dumps(
            {
                "accuracy": 0.91,
                "false_negative_rate": 0.08,
                "false_positive_rate": 0.12,
                "quality_gate": None,
            }
        ),
        json.dumps(
            {
                "accuracy": 0.91,
                "false_negative_rate": 0.08,
                "false_positive_rate": 0.12,
                "quality_gate": {"confidence_threshold": 0.72},
            }
        ),
        json.dumps(
            {
                "accuracy": 0.91,
                "false_negative_rate": 0.08,
                "false_positive_rate": 0.12,
                "quality_gate": {
                    "approved": False,
                    "confidence_threshold": 0.72,
                },
            }
        ),
    ],
)
def test_malformed_or_incomplete_report_preserves_active(
    tmp_path: Path, payload: str
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    metrics.write_text(payload, encoding="utf-8")
    seed_active(output)

    with pytest.raises(ValueError):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)

    assert_active_unchanged(output)


def test_invalid_image_in_dataset_preserves_active(tmp_path: Path) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    image = dataset / "test" / CLASS_NAMES[-1] / f"test-{CLASS_NAMES[-1]}.png"
    image.write_bytes(b"not-an-image")
    seed_active(output)

    with pytest.raises(ValueError, match="Imagem invalida"):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)

    assert_active_unchanged(output)


def test_invalid_dataset_is_rejected_before_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    shutil.rmtree(dataset / "test" / CLASS_NAMES[-1])
    seed_active(output)

    def unexpected_hash(_root: Path) -> str:
        raise AssertionError("dataset_hash nao deveria ser executado")

    monkeypatch.setattr(promover_modelo, "dataset_hash", unexpected_hash)
    with pytest.raises(ValueError, match="Dataset invalido"):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)
    assert_active_unchanged(output)


@pytest.mark.parametrize("failure_point", ["copy", "manifest"])
def test_staging_failure_preserves_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    seed_active(output)

    if failure_point == "copy":
        monkeypatch.setattr(
            promover_modelo.shutil,
            "copy2",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("copy failed")),
        )
    else:
        monkeypatch.setattr(
            ModelManifest,
            "save",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("save failed")),
        )

    with pytest.raises(OSError):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)
    assert_active_unchanged(output)


def test_swap_failure_restores_active(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model, metrics, dataset, output = inputs(tmp_path)
    seed_active(output)
    real_replace = os.replace
    calls = 0

    def fail_second_replace(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("swap failed")
        real_replace(source, destination)

    monkeypatch.setattr(promover_modelo.os, "replace", fail_second_replace)
    with pytest.raises(OSError, match="swap failed"):
        promover_modelo.promote_model(model, metrics, dataset, 224, output)
    assert_active_unchanged(output)
