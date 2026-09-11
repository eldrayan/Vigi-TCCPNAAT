#!/usr/bin/env python3
"""Valida o dataset externo sem altera-lo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_lifecycle.dataset_validation import validate_dataset  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("dataset/vigi-cls"))
    parser.add_argument("--no-verify-images", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    report = validate_dataset(args.dataset, verify_images=not args.no_verify_images)
    payload = json.dumps(report.as_dict(), indent=2, ensure_ascii=False)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
