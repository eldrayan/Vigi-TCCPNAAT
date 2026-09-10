#!/usr/bin/env python3
"""Executa uma inspecao por imagem ou por captura de camera."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.inference import InferenceEngine  # noqa: E402


def capture_frame(backend: str, camera_id: int, width: int, height: int):
    if backend == "picamera2":
        from edge.acquisition.backends.picamera2_camera import Picamera2Camera

        camera = Picamera2Camera(camera_id, width, height, 20, 2.0)
    else:
        from edge.acquisition import load_opencv
        from edge.acquisition.backends.opencv_camera import OpenCVCamera

        cv2 = load_opencv()
        camera = OpenCVCamera(cv2, camera_id, width, height, 20)
    try:
        ok, frame = camera.read()
        if not ok or frame is None:
            raise RuntimeError("A camera nao forneceu uma imagem valida")
        return frame
    finally:
        camera.release()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--image", type=Path)
    source.add_argument("--camera", type=int)
    parser.add_argument(
        "--backend", choices=("opencv", "picamera2"), default="picamera2"
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--threshold", type=float)
    args = parser.parse_args(argv)

    try:
        engine = InferenceEngine.from_manifest(args.manifest, args.threshold)
        if args.image:
            if not args.image.is_file():
                raise RuntimeError(f"Imagem nao encontrada: {args.image}")
            image = str(args.image)
        else:
            image = capture_frame(args.backend, args.camera, args.width, args.height)
        decision = engine.inspect(image)
    except Exception as exc:
        print(json.dumps({"erro": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(decision.as_dict(), indent=2, ensure_ascii=False))
    return 0 if decision.codigo != "ERRO_INFERENCIA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
