#!/usr/bin/env python3
"""Cria o manifesto do modelo aprovado para posterior versionamento no DVC."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.dataset_validation import dataset_hash  # noqa: E402
from model_lifecycle.inspection_classes import CLASS_NAMES  # noqa: E402
from model_lifecycle.manifest import ModelManifest  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--format", choices=("pytorch", "tflite"), required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--output", type=Path, default=Path("models/active"))
    args = parser.parse_args(argv)

    if not args.model.is_file() or not args.metrics.is_file():
        parser.error("Modelo e arquivo de metricas devem existir")
    metrics_payload = json.loads(args.metrics.read_text(encoding="utf-8"))
    metrics = {
        key: float(metrics_payload[key])
        for key in ("accuracy", "false_negative_rate", "false_positive_rate")
    }
    if (
        metrics["accuracy"] < 0.90
        or metrics["false_negative_rate"] > 0.10
        or metrics["false_positive_rate"] > 0.15
    ):
        print("[ERRO] O modelo nao satisfaz o quality gate.", file=sys.stderr)
        return 1

    try:
        import ultralytics
    except ModuleNotFoundError:
        ultralytics_version = "unknown"
    else:
        ultralytics_version = ultralytics.__version__

    args.output.mkdir(parents=True, exist_ok=True)
    suffix = ".pt" if args.format == "pytorch" else ".tflite"
    target = args.output / f"vigi-yolov8n-cls{suffix}"
    shutil.copy2(args.model, target)
    manifest = ModelManifest(
        model_path=target.name,
        format=args.format,
        classes=CLASS_NAMES,
        confidence_threshold=args.threshold,
        image_size=args.imgsz,
        dataset_hash=dataset_hash(args.dataset),
        ultralytics_version=ultralytics_version,
        metrics=metrics,
    )
    manifest_path = args.output / "manifest.json"
    manifest.save(manifest_path)
    print(json.dumps({"model": str(target), "manifest": str(manifest_path)}, indent=2))
    print("[INFO] Execute 'dvc add models' e 'dvc push' para publicar a promocao.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
