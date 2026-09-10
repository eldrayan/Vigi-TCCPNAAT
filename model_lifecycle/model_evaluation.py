"""Execucao e persistencia da avaliacao do modelo."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .dataset_validation import IMAGE_SUFFIXES
from .inspection_classes import CLASS_NAMES, canonical_class
from .quality_metrics import Prediction, QualityMetrics, calculate_metrics, gate_passes


def collect_predictions(
    model: Any, split_dir: Path, image_size: int
) -> list[Prediction]:
    predictions: list[Prediction] = []
    for expected in CLASS_NAMES:
        images = sorted(
            path
            for path in (split_dir / expected).rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        for image in images:
            results = model.predict(source=str(image), imgsz=image_size, verbose=False)
            if not results or results[0].probs is None:
                raise RuntimeError(f"Sem probabilidades para {image}")
            result = results[0]
            class_id = int(result.probs.top1)
            predictions.append(
                Prediction(
                    expected=expected,
                    predicted=canonical_class(str(result.names[class_id])),
                    confidence=float(result.probs.top1conf),
                    path=str(image),
                )
            )
    return predictions


def write_predictions(path: Path, predictions: list[Prediction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("path", "expected", "predicted", "confidence")
        )
        writer.writeheader()
        for prediction in predictions:
            writer.writerow(prediction.__dict__)


def write_metrics(
    path: Path, metrics: QualityMetrics, provisional: bool, threshold: float
) -> None:
    payload = metrics.as_dict()
    payload["quality_gate"] = {
        "accuracy_min": 0.90,
        "false_negative_rate_max": 0.10,
        "false_positive_rate_max": 0.15,
        "provisional": provisional,
        "approved": gate_passes(metrics),
        "confidence_threshold": threshold,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def render_confusion_matrix(path: Path, metrics: QualityMetrics) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return
    figure, axis = plt.subplots(figsize=(8, 7))
    image = axis.imshow(metrics.confusion_matrix, cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set_xticks(range(len(CLASS_NAMES)), [name[3:] for name in CLASS_NAMES])
    axis.set_yticks(range(len(CLASS_NAMES)), [name[3:] for name in CLASS_NAMES])
    axis.set_xlabel("Predita")
    axis.set_ylabel("Real")
    axis.set_title("Matriz de confusao — Vigi")
    for row, values in enumerate(metrics.confusion_matrix):
        for column, value in enumerate(values):
            axis.text(column, row, str(value), ha="center", va="center")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def evaluate_predictions(
    predictions: list[Prediction], threshold: float
) -> QualityMetrics:
    return calculate_metrics(predictions, threshold)
