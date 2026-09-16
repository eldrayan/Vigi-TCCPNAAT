#!/usr/bin/env python3
"""
Descrição: Inicia a inspeção contínua acionada pelo sensor fotoelétrico.
Autor: Leôncio Ferreira
"""

from __future__ import annotations

import argparse
import os
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


def readiness_ok(name: str, detail: str) -> None:
    print(f"  ✓ {name}: {detail}")


def readiness_error(name: str, error: Exception) -> None:
    print(f"  ✗ {name}: {error}", file=sys.stderr)


def check_broker(host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=3):
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path("models/active/manifest.json")
    )
    parser.add_argument("--mqtt-host", default="localhost")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument(
        "--mqtt-username", default=os.getenv("MQTT_EDGE_USERNAME")
    )
    parser.add_argument(
        "--mqtt-password", default=os.getenv("MQTT_EDGE_PASSWORD")
    )
    parser.add_argument("--station-code", default="ESTACAO_01")
    parser.add_argument("--device-id", default="ESTACAO_01")
    parser.add_argument("--batch-code", default="LOTE_01")
    parser.add_argument("--gpio-pin", type=int, default=17)
    parser.add_argument("--debounce-ms", type=float, default=50)
    parser.add_argument(
        "--capture-delay-ms",
        type=float,
        default=0.0,
        help="atraso entre o sensor e a captura, em milissegundos",
    )
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument(
        "--exposure-us",
        type=int,
        default=None,
        help="tempo de exposição manual em microssegundos; ausente mantém AE",
    )
    parser.add_argument(
        "--analogue-gain",
        type=float,
        default=4.0,
        help="ganho analógico usado com --exposure-us (padrão: 4.0)",
    )
    parser.add_argument(
        "--awb-mode",
        choices=("auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"),
        default="auto",
        help="perfil de balanço de branco da câmera (padrão: auto)",
    )
    parser.add_argument(
        "--backend", choices=("picamera2", "opencv", "auto"), default="picamera2"
    )
    parser.add_argument(
        "--outbox-path", type=Path, default=Path("data/edge-outbox.db")
    )
    parser.add_argument(
        "--save-captures",
        action="store_true",
        help="salva o quadro de cada inspeção em --capture-dir",
    )
    parser.add_argument(
        "--capture-dir",
        type=Path,
        default=Path("captures"),
        help="diretório das imagens salvas (padrão: captures)",
    )
    parser.add_argument("--max-inspections", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        raise SystemExit("width, height e fps devem ser positivos")
    if args.exposure_us is not None and args.exposure_us <= 0:
        raise SystemExit("exposure-us deve ser positivo")
    if args.analogue_gain <= 0:
        raise SystemExit("analogue-gain deve ser positivo")
    if args.capture_delay_ms < 0:
        raise SystemExit("capture-delay-ms não pode ser negativo")

    print("\nDiagnóstico de prontidão — Estação 01")
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
