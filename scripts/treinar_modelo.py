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


def create_no_augmentation_trainer(
    trainer_base: type, dataset_type: type
) -> type:
    """Cria o trainer que carrega o dataset exportado sem augmentation adicional."""

    class NoAugmentationClassificationTrainer(trainer_base):
        def build_dataset(
            self, img_path: str, mode: str = "train", batch: int | None = None
        ) -> object:
            del batch  # Mantem a assinatura esperada pelo Ultralytics 8.4.146.
            return dataset_type(
                root=img_path,
                args=self.args,
                augment=False,
                prefix=mode,
            )

    return NoAugmentationClassificationTrainer


def train_model(
    dataset: Path,
    config_path: Path,
    output: Path,
    yolo_type: type,
    trainer_base: type,
    dataset_type: type,
    ultralytics_version: str,
) -> dict[str, object]:
    """Treina, copia o checkpoint indicado pelo trainer e grava seu resumo."""
    config = load_config(config_path)
    model_name = str(config.pop("model"))
    model = yolo_type(model_name)
    trainer_type = create_no_augmentation_trainer(trainer_base, dataset_type)
    model.train(data=str(dataset.resolve()), trainer=trainer_type, **config)
    trainer = getattr(model, "trainer", None)
    if trainer is None:
        raise RuntimeError("Trainer indisponivel apos o treinamento")
    save_dir = Path(trainer.save_dir)
    best_path = Path(trainer.best)
    if not best_path.is_file():
        raise FileNotFoundError(f"Checkpoint nao gerado: {best_path}")

    output.mkdir(parents=True, exist_ok=True)
    run_name = str(config.get("name", "training"))
    candidate = output / f"vigi-yolov8n-cls-{run_name}.pt"
    shutil.copy2(best_path, candidate)
    summary = {
        "checkpoint": str(candidate),
        "run_directory": str(save_dir),
        "dataset_hash": dataset_hash(dataset),
        "ultralytics_version": ultralytics_version,
        "config": config,
    }
    summary_path = save_dir / "vigi-training-summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("training_configuration/training-baseline.yaml"),
    )
    parser.add_argument("--output", type=Path, default=Path("models/candidates"))
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
        from ultralytics.data.dataset import ClassificationDataset
        from ultralytics.models.yolo.classify.train import ClassificationTrainer
    except ModuleNotFoundError as exc:
        print(f"[ERRO] Dependencia de treino ausente: {exc}", file=sys.stderr)
        return 1
    if not torch.cuda.is_available():
        print("[ERRO] CUDA nao esta disponivel para o treino oficial.", file=sys.stderr)
        return 1

    try:
        summary = train_model(
            args.dataset,
            args.config,
            args.output,
            YOLO,
            ClassificationTrainer,
            ClassificationDataset,
            ultralytics.__version__,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("[INFO] Execute 'dvc add dataset/vigi-cls models' e 'dvc push'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
