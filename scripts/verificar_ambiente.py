#!/usr/bin/env python3
"""Verifica Python, CUDA e ferramentas necessarias antes do treino."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys


def main() -> int:
    checks: dict[str, object] = {
        "python": sys.version.split()[0],
        "python_supported": (3, 11) <= sys.version_info[:2] < (3, 13),
        "dvc": shutil.which("dvc") is not None,
        "ssh": shutil.which("ssh") is not None,
        "ultralytics": importlib.util.find_spec("ultralytics") is not None,
    }
    try:
        import torch

        checks["torch"] = torch.__version__
        checks["cuda_available"] = torch.cuda.is_available()
        checks["cuda_device"] = (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        )
    except ModuleNotFoundError:
        checks["torch"] = None
        checks["cuda_available"] = False
        checks["cuda_device"] = None
    if checks["dvc"]:
        result = subprocess.run(
            ["dvc", "remote", "list"], capture_output=True, text=True, check=False
        )
        checks["dvc_remote"] = result.stdout.strip()
    print(json.dumps(checks, indent=2, ensure_ascii=False))
    required = (
        checks["python_supported"],
        checks["dvc"],
        checks["ssh"],
        checks["ultralytics"],
        checks["cuda_available"],
    )
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
