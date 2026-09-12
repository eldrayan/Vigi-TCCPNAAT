#!/usr/bin/env python3
"""Reavalia no CI o modelo ativo e bloqueia regressoes de qualidade."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.manifest import ModelManifest  # noqa: E402
from model_lifecycle.model_evaluation import (  # noqa: E402
    collect_predictions,
    evaluate_predictions,
    render_confusion_matrix,
    write_metrics,
    write_predictions,
)
from model_lifecycle.quality_metrics import gate_passes  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path("models/active/manifest.json")
    )
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument("--output", type=Path, default=Path("reports/model-gate"))
    args = parser.parse_args(argv)

    manifest = ModelManifest.load(args.manifest)
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError:
        print("[ERRO] Ultralytics nao esta instalado", file=sys.stderr)
        return 1
    model = YOLO(str(manifest.resolve_model_path(args.manifest)), task="classify")
    predictions = collect_predictions(model, args.dataset / "test", manifest.image_size)
    metrics = evaluate_predictions(predictions, manifest.confidence_threshold)
    provisional = metrics.sample_count < 200
    args.output.mkdir(parents=True, exist_ok=True)
    write_predictions(args.output / "predictions.csv", predictions)
    write_metrics(
        args.output / "metrics.json",
        metrics,
        provisional,
        manifest.confidence_threshold,
    )
    render_confusion_matrix(args.output / "confusion-matrix.png", metrics)
    if provisional:
        print("::warning::Amostra inferior a 200 imagens; aprovacao apenas provisoria.")
    if not gate_passes(metrics):
        print(f"[FALHA] Quality gate reprovado: {metrics.as_dict()}", file=sys.stderr)
        return 1
    print(f"[OK] Quality gate aprovado: {metrics.as_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
