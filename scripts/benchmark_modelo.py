#!/usr/bin/env python3
"""Mede a latencia do modelo no hardware Edge real."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.inference import InferenceEngine  # noqa: E402
from edge.inference.schemas import InspectionDecision  # noqa: E402
from model_lifecycle.dataset_validation import IMAGE_SUFFIXES  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * fraction), len(ordered) - 1)
    return ordered[index]


def build_report(
    model_format: str,
    requested_runs: int,
    requested_warmup: int,
    warmup_results: list[InspectionDecision],
    measured_results: list[InspectionDecision],
) -> dict[str, object]:
    """Consolida o benchmark sem tratar decisoes de negocio como falhas tecnicas."""
    warmup_errors = sum(
        result.technical_failure_type == "ERRO_INFERENCIA"
        for result in warmup_results
    )
    inference_errors = sum(
        result.technical_failure_type == "ERRO_INFERENCIA"
        for result in measured_results
    )
    successful_results = [
        result
        for result in measured_results
        if result.technical_failure_type != "ERRO_INFERENCIA"
    ]
    latencies = [result.processing_time_ms for result in successful_results]
    within_500ms = sum(latency <= 500 for latency in latencies)
    within_500ms_ratio = within_500ms / requested_runs

    if latencies:
        mean_ms: float | None = statistics.fmean(latencies)
        p50_ms: float | None = percentile(latencies, 0.50)
        p95_ms: float | None = percentile(latencies, 0.95)
        max_ms: float | None = max(latencies)
    else:
        mean_ms = p50_ms = p95_ms = max_ms = None

    latency_gate = (
        warmup_errors == 0
        and inference_errors == 0
        and within_500ms_ratio >= 0.95
        and max_ms is not None
        and max_ms <= 1000
    )
    return {
        "format": model_format,
        "runs": requested_runs,
        "warmup": requested_warmup,
        "successful_runs": len(successful_results),
        "inference_errors": inference_errors,
        "warmup_errors": warmup_errors,
        "within_500ms_ratio": within_500ms_ratio,
        "mean_ms": mean_ms,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "max_ms": max_ms,
        "latency_gate": latency_gate,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--images", type=Path, default=Path("dataset/vigi-cls/test"))
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.runs < 1 or args.warmup < 0:
        parser.error("runs deve ser positivo e warmup nao negativo")

    images = sorted(
        path
        for path in args.images.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not images:
        parser.error(f"Nenhuma imagem encontrada em {args.images}")
    engine = InferenceEngine.from_manifest(args.manifest)

    warmup_results = [
        engine.inspect(str(images[index % len(images)]))
        for index in range(args.warmup)
    ]
    measured_results = [
        engine.inspect(str(images[index % len(images)]))
        for index in range(args.runs)
    ]
    payload = build_report(
        engine.manifest.format,
        args.runs,
        args.warmup,
        warmup_results,
        measured_results,
    )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if payload["latency_gate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
