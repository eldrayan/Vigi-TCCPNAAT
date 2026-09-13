#!/usr/bin/env python3
"""Executa uma inspeção por imagem ou por captura de câmera."""

from __future__ import annotations

import argparse
import json
import socket
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.inference import InferenceEngine, InspectionDecision  # noqa: E402
from edge.messaging import (  # noqa: E402
    InspectionEvent,
    InspectionOutbox,
    MQTTInspectionPublisher,
    MQTTOperationalContextReceiver,
    OperationalContext,
)


def load_operational_context(
    host: str, port: int, device_id: str
) -> OperationalContext:
    return MQTTOperationalContextReceiver(host, port, device_id).receive()


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
    parser.add_argument("--mqtt-host")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--device-id", default=socket.gethostname())
    parser.add_argument(
        "--outbox-path",
        type=Path,
        default=Path("data/edge-outbox.db"),
    )
    args = parser.parse_args(argv)

    try:
        engine = InferenceEngine.from_manifest(args.manifest)
        capture_error = False
        if args.image:
            if not args.image.is_file():
                raise RuntimeError(f"Imagem nao encontrada: {args.image}")
            image = str(args.image)
        else:
            try:
                image = capture_frame(
                    args.backend, args.camera, args.width, args.height
                )
            except Exception:
                capture_error = True
                decision = InspectionDecision(
                    result="NAO_CONFORME",
                    category="FALHA_TECNICA",
                    nonconformity_type=None,
                    technical_failure_type="ERRO_CAPTURA",
                    confidence=None,
                    processing_time_ms=0,
                    model_format=engine.manifest.format,
                )
        if not capture_error:
            decision = engine.inspect(image)
        context = None
        outbox = None
        if args.mqtt_host:
            outbox = InspectionOutbox(args.outbox_path)
            try:
                context = load_operational_context(
                    args.mqtt_host, args.mqtt_port, args.device_id
                )
                outbox.save_context(context)
            except (ConnectionError, OSError, TimeoutError):
                context = outbox.load_context()
                if context is None:
                    raise RuntimeError(
                        "Sem configuração local de estação e lote para operar offline."
                    ) from None
        event = InspectionEvent.from_decision(decision, context=context)
        if args.mqtt_host and context is not None and outbox is not None:
            publisher = MQTTInspectionPublisher(
                host=args.mqtt_host,
                port=args.mqtt_port,
                topic=context.inspections_topic,
            )
            outbox.enqueue(event)
            outbox.deliver(publisher)
            outbox.purge_expired(
                now=datetime.now(UTC),
                retention=timedelta(days=30),
            )
    except Exception as exc:
        print(json.dumps({"erro": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(event.as_dict(), indent=2, ensure_ascii=False))
    return 0 if decision.technical_failure_type != "ERRO_INFERENCIA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
