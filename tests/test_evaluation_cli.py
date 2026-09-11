"""Regressoes da CLI de calibracao e avaliacao final."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from model_lifecycle.model_evaluation import load_calibration_threshold
from model_lifecycle.quality_metrics import QualityMetrics
from scripts import avaliar_modelo


def metrics() -> QualityMetrics:
    return QualityMetrics(
        accuracy=1.0,
        false_negative_rate=0.0,
        false_positive_rate=0.0,
        coverage=1.0,
        sample_count=4,
        confusion_matrix=[[1, 0, 0, 0] for _ in range(4)],
        per_class_accuracy={},
    )


@pytest.mark.parametrize(
    "value", [True, "0.7", None, float("nan"), float("inf"), -0.1, 1.1]
)
def test_calibration_report_rejects_invalid_thresholds(
    tmp_path: Path, value: object
) -> None:
    report = tmp_path / "metrics.json"
    report.write_text(
        json.dumps({"quality_gate": {"confidence_threshold": value}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="confidence_threshold"):
        load_calibration_threshold(report)


def test_calibration_report_loads_valid_threshold(tmp_path: Path) -> None:
    report = tmp_path / "metrics.json"
    report.write_text(
        json.dumps({"quality_gate": {"confidence_threshold": 0.72}}),
        encoding="utf-8",
    )
    assert load_calibration_threshold(report) == 0.72


@pytest.mark.parametrize(
    "content, message",
    [
        ("not-json", "JSON de calibracao invalido"),
        ("[]", "objeto JSON"),
        ("{}", "quality_gate"),
        ('{"quality_gate": []}', "quality_gate"),
        ('{"quality_gate": {}}', "confidence_threshold"),
    ],
)
def test_calibration_report_rejects_invalid_structure(
    tmp_path: Path, content: str, message: str
) -> None:
    report = tmp_path / "metrics.json"
    report.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_calibration_threshold(report)


def test_calibration_report_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="nao encontrado"):
        load_calibration_threshold(tmp_path / "missing.json")


def install_fake_ultralytics(monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.ModuleType("ultralytics")
    module.YOLO = lambda *_args, **_kwargs: object()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "ultralytics", module)


def test_calibrate_uses_val_and_calibration_default_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = tmp_path / "model.pt"
    model.touch()
    captured: dict[str, object] = {}
    install_fake_ultralytics(monkeypatch)

    def collect(_model: object, split: Path, _size: int) -> list[object]:
        captured["split"] = split
        return []

    monkeypatch.setattr(
        avaliar_modelo,
        "collect_predictions",
        collect,
    )
    monkeypatch.setattr(
        avaliar_modelo, "choose_threshold", lambda _: (0.72, metrics())
    )

    def write_predictions(path: Path, _: list[object]) -> None:
        captured["output"] = path.parent

    monkeypatch.setattr(avaliar_modelo, "write_predictions", write_predictions)
    monkeypatch.setattr(avaliar_modelo, "write_metrics", lambda *_: None)
    monkeypatch.setattr(avaliar_modelo, "render_confusion_matrix", lambda *_: None)

    result = avaliar_modelo.main(
        ["--model", str(model), "--dataset", str(tmp_path), "--calibrate"]
    )
    assert result == 0
    assert captured["split"] == tmp_path / "val"
    assert captured["output"] == Path("reports/calibration")


def test_final_evaluation_uses_test_and_report_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = tmp_path / "model.pt"
    model.touch()
    report = tmp_path / "calibration.json"
    report.write_text(
        json.dumps({"quality_gate": {"confidence_threshold": 0.72}}),
        encoding="utf-8",
    )
    captured: dict[str, object] = {}
    install_fake_ultralytics(monkeypatch)

    def collect(_model: object, split: Path, _size: int) -> list[object]:
        captured["split"] = split
        return []

    monkeypatch.setattr(
        avaliar_modelo,
        "collect_predictions",
        collect,
    )

    def evaluate(_: list[object], threshold: float) -> QualityMetrics:
        captured["threshold"] = threshold
        return metrics()

    monkeypatch.setattr(
        avaliar_modelo,
        "evaluate_predictions",
        evaluate,
    )
    monkeypatch.setattr(avaliar_modelo, "write_predictions", lambda *_: None)
    monkeypatch.setattr(avaliar_modelo, "write_metrics", lambda *_: None)
    monkeypatch.setattr(avaliar_modelo, "render_confusion_matrix", lambda *_: None)

    result = avaliar_modelo.main(
        [
            "--model",
            str(model),
            "--dataset",
            str(tmp_path),
            "--calibration-report",
            str(report),
        ]
    )
    assert result == 0
    assert captured == {"split": tmp_path / "test", "threshold": 0.72}


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--calibrate", "--calibration-report", "x"],
        ["--split", "val", "--calibrate"],
        ["--threshold", "0.7", "--calibrate"],
    ],
)
def test_evaluation_rejects_ambiguous_or_legacy_modes(
    tmp_path: Path, args: list[str]
) -> None:
    model = tmp_path / "model.pt"
    model.touch()
    with pytest.raises(SystemExit) as exc_info:
        avaliar_modelo.main(["--model", str(model), *args])
    assert exc_info.value.code == 2
