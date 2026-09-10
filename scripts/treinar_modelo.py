#!/usr/bin/env python3
"""Executa fine-tuning local do YOLOv8n-cls sem augmentation adicional."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.dataset_validation import (  # noqa: E402
    dataset_hash,
    validate_dataset,
)


def load_config(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Configuracao invalida: {path}")
    if data.get("augment") is not False:
        raise ValueError("augment deve permanecer false; o aumento e externo")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("training_configuration/training-baseline.yaml"),
    )
    parser.add_argument("--output", type=Path, default=Path("models/candidates"))
    parser.add_argument("--export-tflite", action="store_true")
    args = parser.parse_args(argv)

    report = validate_dataset(args.dataset)
    if not report.valid:
        print(
            json.dumps(report.as_dict(), indent=2, ensure_ascii=False), file=sys.stderr
        )
        return 1

    try:
        import torch
        import ultralytics
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        print(f"[ERRO] Dependencia de treino ausente: {exc}", file=sys.stderr)
        return 1
    if not torch.cuda.is_available():
        print("[ERRO] CUDA nao esta disponivel para o treino oficial.", file=sys.stderr)
        return 1

    config = load_config(args.config)
    model_name = str(config.pop("model"))
    model = YOLO(model_name)
    results = model.train(data=str(args.dataset.resolve()), **config)
    save_dir = Path(results.save_dir)
    best_path = save_dir / "weights" / "best.pt"
    if not best_path.exists():
        print(f"[ERRO] Checkpoint nao gerado: {best_path}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    run_name = str(config.get("name", "training"))
    promoted_pt = args.output / f"vigi-yolov8n-cls-{run_name}.pt"
    shutil.copy2(best_path, promoted_pt)

    exported: str | None = None
    if args.export_tflite:
        export_model = YOLO(str(promoted_pt), task="classify")
        exported_path = Path(
            export_model.export(format="tflite", imgsz=int(config["imgsz"]))
        )
        if exported_path.is_dir():
            candidates = sorted(exported_path.rglob("*.tflite"))
            if not candidates:
                print(
                    f"[ERRO] Exportacao nao produziu TFLite em {exported_path}",
                    file=sys.stderr,
                )
                return 1
            float32 = [path for path in candidates if "float32" in path.name]
            exported_path = float32[0] if float32 else candidates[0]
        target = args.output / f"vigi-yolov8n-cls-{run_name}-fp32.tflite"
        shutil.copy2(exported_path, target)
        exported = str(target)

    summary = {
        "checkpoint": str(promoted_pt),
        "tflite": exported,
        "run_directory": str(save_dir),
        "dataset_hash": dataset_hash(args.dataset),
        "ultralytics_version": ultralytics.__version__,
        "config": config,
    }
    summary_path = save_dir / "vigi-training-summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("[INFO] Execute 'dvc add dataset/vigi-cls models' e 'dvc push'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
