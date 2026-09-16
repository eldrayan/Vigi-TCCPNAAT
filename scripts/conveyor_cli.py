"""
Descrição: Define e valida os argumentos da estação de inspeção.
Autor: Leôncio Ferreira
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inicia a inspeção contínua acionada pelo sensor fotoelétrico."
    )
    parser.add_argument(
        "--manifest", type=Path, default=Path("models/active/manifest.json")
    )
    parser.add_argument("--mqtt-host", default="localhost")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-username", default=os.getenv("MQTT_EDGE_USERNAME"))
    parser.add_argument("--mqtt-password", default=os.getenv("MQTT_EDGE_PASSWORD"))
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
        help="ganho analógico usado com --exposure-us",
    )
    parser.add_argument(
        "--awb-mode",
        choices=("auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"),
        default="auto",
        help="perfil de balanço de branco da câmera",
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
        help="diretório das imagens salvas",
    )
    parser.add_argument("--max-inspections", type=int)
    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        raise SystemExit("width, height e fps devem ser positivos")
    if args.exposure_us is not None and args.exposure_us <= 0:
        raise SystemExit("exposure-us deve ser positivo")
    if args.analogue_gain <= 0:
        raise SystemExit("analogue-gain deve ser positivo")
    if args.capture_delay_ms < 0:
        raise SystemExit("capture-delay-ms não pode ser negativo")
