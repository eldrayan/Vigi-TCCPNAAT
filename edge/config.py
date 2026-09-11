"""Configurações da aplicação executada na Raspberry Pi."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


def default_session_id() -> str:
    return datetime.now(UTC).strftime("sessao_%Y%m%dT%H%M%SZ")


@dataclass(frozen=True)
class CollectionConfig:
    backend: str
    camera: int
    width: int
    height: int
    fps: int
    warmup_seconds: float
    output: Path
    session: str
    burst_interval: float
    blur_threshold: float
    jpeg_quality: int
    guide_width: float
    guide_height: float
    crop_guide: bool
    headless: bool


def parse_collection_config(argv: list[str] | None = None) -> CollectionConfig:
    parser = argparse.ArgumentParser(
        description="Coleta assistida do dataset de garrafas do Vigi"
    )
    parser.add_argument(
        "--backend",
        choices=("picamera2", "auto", "opencv"),
        default="picamera2",
        help="picamera2 captura diretamente da câmera CSI; opencv é para USB",
    )
    parser.add_argument("--camera", type=int, default=0, help="índice da câmera")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument(
        "--warmup-seconds",
        type=float,
        default=2.0,
        help="tempo para exposição e balanço de branco estabilizarem",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("dataset/raw"), help="diretório de saída"
    )
    parser.add_argument("--session", default=default_session_id())
    parser.add_argument(
        "--burst-interval",
        type=float,
        default=0.35,
        help="intervalo entre imagens no modo burst, em segundos",
    )
    parser.add_argument(
        "--blur-threshold",
        type=float,
        default=80.0,
        help="variância mínima do Laplaciano; 0 desativa o filtro",
    )
    parser.add_argument("--jpeg-quality", type=int, default=95)
    parser.add_argument("--guide-width", type=float, default=0.55)
    parser.add_argument("--guide-height", type=float, default=0.88)
    parser.add_argument(
        "--crop-guide",
        action="store_true",
        help="salva somente a região interna da guia",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="não abre janela; recebe os controles diretamente pelo terminal",
    )
    args = parser.parse_args(argv)

    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        parser.error("width, height e fps devem ser positivos")
    if args.burst_interval <= 0:
        parser.error("burst-interval deve ser positivo")
    if args.warmup_seconds < 0:
        parser.error("warmup-seconds não pode ser negativo")
    if not 1 <= args.jpeg_quality <= 100:
        parser.error("jpeg-quality deve estar entre 1 e 100")
    if not 0.1 <= args.guide_width <= 1.0:
        parser.error("guide-width deve estar entre 0.1 e 1.0")
    if not 0.1 <= args.guide_height <= 1.0:
        parser.error("guide-height deve estar entre 0.1 e 1.0")

    return CollectionConfig(**vars(args))
