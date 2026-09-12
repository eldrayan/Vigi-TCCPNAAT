#!/usr/bin/env python3
"""Cria o manifesto do modelo aprovado para posterior versionamento no DVC."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import tempfile
from numbers import Real
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.dataset_validation import (  # noqa: E402
    dataset_hash,
    validate_dataset,
)
from model_lifecycle.inspection_classes import CLASS_NAMES  # noqa: E402
from model_lifecycle.manifest import ModelManifest  # noqa: E402

METRIC_LIMITS = {
    "accuracy": (0.90, None),
    "false_negative_rate": (None, 0.10),
    "false_positive_rate": (None, 0.15),
}
ACTIVE_MODEL_NAME = "vigi-yolov8n-cls.pt"


def _probability(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{field} deve ser um numero real")
    number = float(value)
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{field} deve ser finito e estar entre 0 e 1")
    return number


def _load_metrics(path: Path) -> tuple[dict[str, float], float]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Relatorio de metricas possui JSON invalido: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("A raiz do relatorio de metricas deve ser um objeto JSON")

    metrics: dict[str, float] = {}
    for field, (minimum, maximum) in METRIC_LIMITS.items():
        if field not in payload:
            raise ValueError(f"Metrica obrigatoria ausente: {field}")
        value = _probability(payload[field], field)
        if minimum is not None and value < minimum:
            raise ValueError(f"{field} reprova o quality gate")
        if maximum is not None and value > maximum:
            raise ValueError(f"{field} reprova o quality gate")
        metrics[field] = value

    quality_gate = payload.get("quality_gate")
    if not isinstance(quality_gate, dict):
        raise ValueError("quality_gate deve ser um objeto")
    if "confidence_threshold" not in quality_gate:
        raise ValueError("quality_gate.confidence_threshold ausente")
    threshold = _probability(
        quality_gate["confidence_threshold"],
        "quality_gate.confidence_threshold",
    )
    approved = quality_gate.get("approved")
    if not isinstance(approved, bool):
        raise ValueError("quality_gate.approved deve ser booleano")
    if not approved:
        raise ValueError("O relatorio reprova o quality gate")
    return metrics, threshold


def _replace_active_directory(staging: Path, output: Path) -> None:
    backup = output.parent / f".{output.name}.backup"
    if backup.exists():
        raise ValueError(f"Backup pendente impede a promocao: {backup}")

    had_active = output.exists()
    if had_active:
        if not output.is_dir() or output.is_symlink():
            raise ValueError(f"A saida ativa nao e um diretorio seguro: {output}")
        os.replace(output, backup)
    try:
        os.replace(staging, output)
    except BaseException:
        if had_active:
            os.replace(backup, output)
        raise
    if had_active:
        shutil.rmtree(backup)


def promote_model(
    model: Path,
    metrics_path: Path,
    dataset: Path,
    image_size: int,
    output: Path,
) -> tuple[Path, Path]:
    if not model.is_file():
        raise ValueError(f"Modelo candidato nao encontrado: {model}")
    if model.suffix.lower() != ".pt":
        raise ValueError("O modelo candidato deve ser um checkpoint PyTorch .pt")
    if not metrics_path.is_file():
        raise ValueError(f"Relatorio de metricas nao encontrado: {metrics_path}")
    if (
        isinstance(image_size, bool)
        or not isinstance(image_size, int)
        or image_size <= 0
    ):
        raise ValueError("imgsz deve ser um inteiro positivo")

    metrics, threshold = _load_metrics(metrics_path)
    dataset_report = validate_dataset(dataset, verify_images=True)
    if not dataset_report.valid:
        details = "; ".join(dataset_report.errors)
        raise ValueError(f"Dataset invalido: {details}")
    validated_dataset_hash = dataset_hash(dataset)

    try:
        import ultralytics
    except ModuleNotFoundError:
        ultralytics_version = "unknown"
    else:
        ultralytics_version = ultralytics.__version__

    manifest = ModelManifest(
        model_path=ACTIVE_MODEL_NAME,
        format="pytorch",
        classes=CLASS_NAMES,
        confidence_threshold=threshold,
        image_size=image_size,
        dataset_hash=validated_dataset_hash,
        ultralytics_version=ultralytics_version,
        metrics=metrics,
    )

    output_parent = output.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output_parent)
    )
    try:
        staged_model = staging / ACTIVE_MODEL_NAME
        staged_manifest = staging / "manifest.json"
        shutil.copy2(model, staged_model)
        manifest.save(staged_manifest)
        ModelManifest.load(staged_manifest)
        _replace_active_directory(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    return output / ACTIVE_MODEL_NAME, output / "manifest.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--output", type=Path, default=Path("models/active"))
    args = parser.parse_args(argv)

    try:
        target, manifest_path = promote_model(
            model=args.model,
            metrics_path=args.metrics,
            dataset=args.dataset,
            image_size=args.imgsz,
            output=args.output,
        )
    except (OSError, ValueError) as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"model": str(target), "manifest": str(manifest_path)}, indent=2))
    print("[INFO] Execute 'dvc add models' e 'dvc push' para publicar a promocao.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
