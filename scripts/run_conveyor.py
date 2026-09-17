#!/usr/bin/env python3
"""
Descrição: Inicia a inspeção contínua acionada pelo sensor fotoelétrico.
Autor: Leôncio Ferreira
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.acquisition import (  # noqa: E402
    CameraFactory,
    PhotoelectricSensor,
    load_opencv,
)
from edge.config import CollectionConfig  # noqa: E402
from edge.inference import InferenceEngine  # noqa: E402
from edge.messaging import (  # noqa: E402
    InspectionOutbox,
    MQTTDeviceStatusPublisher,
    MQTTInspectionPublisher,
    OperationalContext,
)
from edge.orchestration import ConveyorOrchestrator  # noqa: E402
from scripts.conveyor_cli import build_parser, validate_arguments  # noqa: E402


def readiness_ok(name: str, detail: str) -> None:
    print(f"  ✓ {name}: {detail}")


def readiness_error(name: str, error: Exception) -> None:
    print(f"  ✗ {name}: {error}", file=sys.stderr)


def check_broker(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=3):
        return


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_arguments(args)

    print(f"\nDiagnóstico de prontidão — {args.station_code}")
    print("-" * 42)
    camera = None
    sensor = None
    try:
        engine = InferenceEngine.from_manifest(args.manifest)
        readiness_ok("Modelo", f"{args.manifest} ({engine.manifest.format})")

        sensor = PhotoelectricSensor(
            pin=args.gpio_pin, debounce_ms=args.debounce_ms
        )
        readiness_ok(
            "Sensor E18-D80NK",
            f"GPIO {args.gpio_pin} com debounce de {args.debounce_ms} ms",
        )

        config = CollectionConfig(
            backend=args.backend,
            camera=args.camera,
            width=args.width,
            height=args.height,
            fps=args.fps,
            warmup_seconds=2,
            output=Path("captures"),
            session=socket.gethostname(),
            burst_interval=0.35,
            blur_threshold=0,
            jpeg_quality=95,
            guide_width=0.55,
            guide_height=0.88,
            crop_guide=False,
            headless=True,
            exposure_us=args.exposure_us,
            analogue_gain=args.analogue_gain,
            awb_mode=args.awb_mode,
        )
        backend = CameraFactory.resolve_backend(args.backend)
        cv2 = load_opencv() if backend == "opencv" else None
        camera = CameraFactory.create(config, cv2, backend)
        ok, _ = camera.read()
        if not ok:
            raise RuntimeError("não foi possível capturar o quadro de teste")
        readiness_ok("Câmera", f"{backend} no dispositivo {args.camera}")
        readiness_ok(
            "Captura",
            f"{args.width}x{args.height} a {args.fps} FPS; "
            + (
                f"exposição {args.exposure_us} µs, ganho {args.analogue_gain:g}"
                if args.exposure_us is not None
                else "exposição automática"
            ),
        )
        readiness_ok(
            "Atraso de captura", f"{args.capture_delay_ms:g} ms após o sensor"
        )
        readiness_ok("Balanço de branco", args.awb_mode)
        readiness_ok(
            "Capturas",
            f"salvas em {args.capture_dir}"
            if args.save_captures
            else "não serão salvas",
        )

        check_broker(args.mqtt_host, args.mqtt_port)
        readiness_ok("Broker MQTT", f"{args.mqtt_host}:{args.mqtt_port}")
    except Exception as error:
        readiness_error("Prontidão", error)
        if sensor is not None:
            sensor.close()
        if camera is not None:
            camera.release()
        return 1

    print("Sistema pronto. Aguardando recipientes no sensor...\n")
    context = OperationalContext(
        station_code=args.station_code, batch_code=args.batch_code
    )
    status = MQTTDeviceStatusPublisher(
        args.mqtt_host,
        device_id=args.device_id,
        port=args.mqtt_port,
        username=args.mqtt_username,
        password=args.mqtt_password,
    )
    status.start(sensor="ONLINE", camera="ONLINE", processing="ONLINE")

    def report_idle(is_idle: bool) -> None:
        status.publish(
            sensor="ONLINE",
            camera="ONLINE",
            processing="IDLE" if is_idle else "ONLINE",
        )

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        outbox=InspectionOutbox(args.outbox_path),
        publisher=MQTTInspectionPublisher(
            args.mqtt_host,
            args.mqtt_port,
            username=args.mqtt_username,
            password=args.mqtt_password,
            client_id=f"vigi-edge-{args.device_id}",
        ),
        context=context,
        on_idle=report_idle,
        save_dir=args.capture_dir if args.save_captures else None,
        capture_delay_s=args.capture_delay_ms / 1000.0,
    )
    try:
        orchestrator.run(max_cycles=args.max_inspections)
    finally:
        status.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
