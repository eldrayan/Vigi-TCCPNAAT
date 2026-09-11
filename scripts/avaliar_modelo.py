#!/usr/bin/env python3
"""Avalia o classificador e aplica o quality gate do Vigi."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.model_evaluation import (  # noqa: E402
    collect_predictions,
    evaluate_predictions,
    load_calibration_threshold,
    render_confusion_matrix,
    write_metrics,
    write_predictions,
)
from model_lifecycle.quality_metrics import choose_threshold, gate_passes  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument("--imgsz", type=int, default=224)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--calibrate", action="store_true")
    mode.add_argument("--calibration-report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    if not args.model.exists():
        parser.error(f"Modelo nao encontrado: {args.model}")
    if args.imgsz <= 0:
        parser.error("--imgsz deve ser positivo")
    split = "val" if args.calibrate else "test"
    output = args.output or Path(
        "reports/calibration" if args.calibrate else "reports/model-gate"
    )
    threshold = 0.0
    if args.calibration_report is not None:
        try:
            threshold = load_calibration_threshold(args.calibration_report)
        except ValueError as exc:
            parser.error(str(exc))
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError:
        print("[ERRO] Ultralytics nao esta instalado", file=sys.stderr)
        return 1

    model = YOLO(str(args.model), task="classify")
    predictions = collect_predictions(model, args.dataset / split, args.imgsz)
    if args.calibrate:
        threshold, metrics = choose_threshold(predictions)
    else:
        metrics = evaluate_predictions(predictions, threshold)

    output.mkdir(parents=True, exist_ok=True)
    provisional = metrics.sample_count < 200
    write_predictions(output / "predictions.csv", predictions)
    write_metrics(output / "metrics.json", metrics, provisional, threshold)
    render_confusion_matrix(output / "confusion-matrix.png", metrics)
    summary = metrics.as_dict()
    summary.update(
        {
            "threshold": threshold,
            "provisional": provisional,
            "approved": gate_passes(metrics),
        }
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if gate_passes(metrics) else 1


if __name__ == "__main__":
    raise SystemExit(main())
