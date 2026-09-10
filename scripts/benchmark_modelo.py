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
from model_lifecycle.dataset_validation import IMAGE_SUFFIXES  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * fraction), len(ordered) - 1)
    return ordered[index]


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

    for index in range(args.warmup):
        engine.inspect(str(images[index % len(images)]))
    latencies = [
        engine.inspect(str(images[index % len(images)])).tempo_processamento_ms
        for index in range(args.runs)
    ]
    payload = {
        "format": engine.manifest.format,
        "runs": args.runs,
        "warmup": args.warmup,
        "mean_ms": statistics.fmean(latencies),
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "max_ms": max(latencies),
    }
    payload["latency_gate"] = payload["p95_ms"] < 500 and payload["max_ms"] < 1000
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if payload["latency_gate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
