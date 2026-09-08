#!/usr/bin/env python3
"""Coleta assistida da base de imagens do Vigi na Raspberry Pi.

O backend principal usa Picamera2 para obter os quadros diretamente da câmera
CSI. O programa não executa classificação, inferência ou treinamento: apenas
organiza JPEGs rotulados para posterior envio a uma plataforma externa.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CLASSES = {
    1: "01_conforme",
    2: "02_sem_tampa",
    3: "03_tampa_torta",
    4: "04_amassado",
}

MANIFEST_FIELDS = (
    "arquivo",
    "classe",
    "sessao",
    "amostra_fisica",
    "grupo",
    "capturado_em_utc",
    "backend",
    "largura",
    "altura",
    "recortada",
    "nitidez",
    "modo",
)


def load_vision_modules() -> tuple[Any, Any]:
    """Carrega dependências pesadas só ao executar a aplicação."""
    try:
        return importlib.import_module("cv2"), importlib.import_module("numpy")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenCV/NumPy não encontrados. Instale com "
            "'sudo apt install python3-opencv python3-numpy' no Raspberry Pi OS."
        ) from exc


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def default_session_id() -> str:
    return utc_now().strftime("sessao_%Y%m%dT%H%M%SZ")


def class_from_key(key: int) -> int | None:
    if ord("1") <= key <= ord("4"):
        return key - ord("0")
    return None


def guide_bounds(
    frame_width: int,
    frame_height: int,
    width_ratio: float,
    height_ratio: float,
) -> tuple[int, int, int, int]:
    guide_width = max(1, int(frame_width * width_ratio))
    guide_height = max(1, int(frame_height * height_ratio))
    x1 = max(0, (frame_width - guide_width) // 2)
    y1 = max(0, (frame_height - guide_height) // 2)
    return x1, y1, min(frame_width, x1 + guide_width), min(
        frame_height, y1 + guide_height
    )


def safe_component(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in value
    ).strip("_")
    return cleaned or "sessao"


@dataclass
class CaptureState:
    session_id: str
    selected_class: int = 1
    burst_enabled: bool = False
    crop_guide: bool = False
    physical_samples: dict[int, int] = field(
        default_factory=lambda: {class_id: 1 for class_id in CLASSES}
    )
    saved_by_class: dict[int, int] = field(
        default_factory=lambda: {class_id: 0 for class_id in CLASSES}
    )
    rejected_blurry: int = 0

    @property
    def class_name(self) -> str:
        return CLASSES[self.selected_class]

    @property
    def physical_sample(self) -> int:
        return self.physical_samples[self.selected_class]

    @property
    def group_id(self) -> str:
        return (
            f"{safe_component(self.session_id)}__{self.class_name}"
            f"__frasco_{self.physical_sample:03d}"
        )

    def select_class(self, class_id: int) -> None:
        if class_id not in CLASSES:
            raise ValueError(f"Classe inválida: {class_id}")
        self.selected_class = class_id
        self.burst_enabled = False

    def next_physical_sample(self) -> None:
        self.physical_samples[self.selected_class] += 1
        self.burst_enabled = False


class OpenCVCapture:
    def __init__(self, cv2: Any, device: int, width: int, height: int, fps: int):
        self.cv2 = cv2
        self.capture = cv2.VideoCapture(device)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, fps)

    def is_opened(self) -> bool:
        return bool(self.capture.isOpened())

    def read(self) -> tuple[bool, Any]:
        return self.capture.read()

    def release(self) -> None:
        self.capture.release()


class Picamera2Capture:
    """Captura diretamente da câmera CSI usando a API oficial Picamera2."""

    def __init__(
        self,
        device: int,
        width: int,
        height: int,
        fps: int,
        warmup_seconds: float,
    ):
        try:
            picamera2_module = importlib.import_module("picamera2")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Picamera2 não foi encontrado. No Raspberry Pi OS, instale "
                "com 'sudo apt install python3-picamera2'."
            ) from exc

        self.camera = picamera2_module.Picamera2(camera_num=device)
        self.started = False
        try:
            configuration = self.camera.create_video_configuration(
                main={"size": (width, height), "format": "RGB888"},
                controls={"FrameRate": float(fps)},
                buffer_count=4,
            )
            self.camera.configure(configuration)
            self.camera.start()
            self.started = True
            if "AfMode" in self.camera.camera_controls:
                libcamera = importlib.import_module("libcamera")
                self.camera.set_controls(
                    {"AfMode": libcamera.controls.AfModeEnum.Continuous}
                )
        except Exception as exc:
            self.camera.close()
            raise RuntimeError(
                f"Não foi possível inicializar a câmera CSI {device} via Picamera2."
            ) from exc
        if warmup_seconds > 0:
            time.sleep(warmup_seconds)

    def is_opened(self) -> bool:
        return self.started

    def read(self) -> tuple[bool, Any]:
        frame = self.camera.capture_array("main")
        return frame is not None, frame

    def release(self) -> None:
        if self.started:
            self.camera.stop()
            self.camera.close()
            self.started = False


class RpicamCapture:
    """Fallback para CSI quando a biblioteca Picamera2 não estiver disponível."""

    def __init__(
        self,
        cv2: Any,
        np: Any,
        camera: int,
        width: int,
        height: int,
        fps: int,
    ):
        executable = shutil.which("rpicam-vid")
        if executable is None:
            raise RuntimeError(
                "rpicam-vid não foi encontrado. Instale rpicam-apps ou use "
                "--backend opencv para uma câmera USB."
            )
        command = [
            executable,
            "-t",
            "0",
            "-n",
            "--codec",
            "mjpeg",
            "--camera",
            str(camera),
            "--width",
            str(width),
            "--height",
            str(height),
            "--framerate",
            str(fps),
            "-o",
            "-",
        ]
        self.cv2 = cv2
        self.np = np
        self.buffer = b""
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

    def is_opened(self) -> bool:
        return self.process.poll() is None and self.process.stdout is not None

    def read(self) -> tuple[bool, Any]:
        if self.process.stdout is None:
            return False, None
        while self.process.poll() is None:
            start = self.buffer.find(b"\xff\xd8")
            end = self.buffer.find(b"\xff\xd9", start + 2) if start >= 0 else -1
            if start >= 0 and end >= 0:
                jpeg = self.buffer[start : end + 2]
                self.buffer = self.buffer[end + 2 :]
                frame = self.cv2.imdecode(
                    self.np.frombuffer(jpeg, dtype=self.np.uint8),
                    self.cv2.IMREAD_COLOR,
                )
                return frame is not None, frame
            chunk = self.process.stdout.read(65536)
            if not chunk:
                break
            self.buffer += chunk
            if len(self.buffer) > 8 * 1024 * 1024:
                marker = self.buffer.rfind(b"\xff\xd8")
                self.buffer = self.buffer[marker:] if marker >= 0 else b""
        return False, None

    def release(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)


class ManifestWriter:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        new_file = not path.exists() or path.stat().st_size == 0
        self.handle = path.open("a", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(self.handle, fieldnames=MANIFEST_FIELDS)
        if new_file:
            self.writer.writeheader()
            self._sync()

    def append(self, row: dict[str, object]) -> None:
        self.writer.writerow(row)
        self._sync()

    def _sync(self) -> None:
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        self.handle.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coleta assistida do dataset de garrafas do Vigi"
    )
    parser.add_argument(
        "--backend",
        choices=("picamera2", "auto", "rpicam", "opencv"),
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
    args = parser.parse_args(argv)
    if args.width <= 0 or args.height <= 0 or args.fps <= 0:
        parser.error("width, height e fps devem ser positivos")
    if args.burst_interval <= 0:
        parser.error("burst-interval deve ser positivo")
    if args.warmup_seconds < 0:
        parser.error("warmup-seconds não pode ser negativo")
    if not 1 <= args.jpeg_quality <= 100:
        parser.error("jpeg-quality deve estar entre 1 e 100")
    if not 0.1 <= args.guide_width <= 1.0 or not 0.1 <= args.guide_height <= 1.0:
        parser.error("guide-width e guide-height devem estar entre 0.1 e 1.0")
    return args


def resolve_backend(requested: str) -> str:
    if requested == "auto":
        try:
            if importlib.util.find_spec("picamera2") is not None:
                return "picamera2"
        except (ImportError, AttributeError, ValueError):
            pass
        return "rpicam" if shutil.which("rpicam-vid") else "opencv"
    return requested


def open_camera(args: argparse.Namespace, cv2: Any, np: Any, backend: str) -> Any:
    if backend == "picamera2":
        camera = Picamera2Capture(
            args.camera,
            args.width,
            args.height,
            args.fps,
            args.warmup_seconds,
        )
    elif backend == "rpicam":
        camera = RpicamCapture(
            cv2, np, args.camera, args.width, args.height, args.fps
        )
    else:
        camera = OpenCVCapture(
            cv2, args.camera, args.width, args.height, args.fps
        )
    if not camera.is_opened():
        camera.release()
        raise RuntimeError(
            f"Não foi possível abrir a câmera {args.camera} com backend {backend}."
        )
    return camera


def sharpness_score(cv2: Any, frame: Any) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def draw_overlay(
    cv2: Any,
    frame: Any,
    state: CaptureState,
    guide: tuple[int, int, int, int],
    score: float,
    threshold: float,
    message: str,
) -> Any:
    preview = frame.copy()
    x1, y1, x2, y2 = guide
    color = (0, 220, 0) if score >= threshold or threshold <= 0 else (0, 80, 255)
    cv2.rectangle(preview, (x1, y1), (x2, y2), color, 2)
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.line(preview, (center_x - 18, center_y), (center_x + 18, center_y), color, 1)
    cv2.line(preview, (center_x, center_y - 18), (center_x, center_y + 18), color, 1)

    mode = "BURST ATIVO" if state.burst_enabled else "MANUAL"
    crop = "ROI" if state.crop_guide else "QUADRO INTEIRO"
    lines = [
        f"Classe [{state.selected_class}]: {state.class_name}",
        f"Frasco fisico: {state.physical_sample:03d} | {mode} | {crop}",
        f"Nitidez: {score:.1f} | Salvas nesta classe: {state.saved_by_class[state.selected_class]}",
        "1-4 classe | ESPACO foto | B burst | N proximo frasco | C recorte | Q sair",
    ]
    overlay_height = 28 * len(lines) + (30 if message else 0)
    cv2.rectangle(preview, (0, 0), (preview.shape[1], overlay_height), (0, 0, 0), -1)
    for index, line in enumerate(lines):
        cv2.putText(
            preview,
            line,
            (12, 24 + index * 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    if message:
        cv2.putText(
            preview,
            message,
            (12, 24 + len(lines) * 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
            cv2.LINE_AA,
        )
    return preview


def save_capture(
    cv2: Any,
    frame: Any,
    state: CaptureState,
    args: argparse.Namespace,
    backend: str,
    guide: tuple[int, int, int, int],
    score: float,
    mode: str,
    manifest: ManifestWriter,
) -> Path | None:
    if args.blur_threshold > 0 and score < args.blur_threshold:
        state.rejected_blurry += 1
        return None

    image = frame
    if state.crop_guide:
        x1, y1, x2, y2 = guide
        image = frame[y1:y2, x1:x2]

    captured_at = utc_now()
    class_dir = args.output / state.class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    sequence = state.saved_by_class[state.selected_class] + 1
    timestamp = captured_at.strftime("%Y%m%dT%H%M%S_%fZ")
    filename = f"{state.group_id}__{timestamp}__{sequence:05d}.jpg"
    path = class_dir / filename
    temporary_path = class_dir / f".{filename}.tmp.jpg"
    ok = cv2.imwrite(
        str(temporary_path), image, [cv2.IMWRITE_JPEG_QUALITY, args.jpeg_quality]
    )
    if not ok:
        return None
    os.replace(temporary_path, path)
    state.saved_by_class[state.selected_class] = sequence
    relative_path = path.relative_to(args.output).as_posix()
    manifest.append(
        {
            "arquivo": relative_path,
            "classe": state.class_name,
            "sessao": state.session_id,
            "amostra_fisica": state.physical_sample,
            "grupo": state.group_id,
            "capturado_em_utc": captured_at.isoformat(),
            "backend": backend,
            "largura": int(image.shape[1]),
            "altura": int(image.shape[0]),
            "recortada": state.crop_guide,
            "nitidez": f"{score:.2f}",
            "modo": mode,
        }
    )
    return path


def print_summary(state: CaptureState, output: Path) -> None:
    print("\nResumo da coleta")
    print(f"  Sessão: {state.session_id}")
    for class_id, class_name in CLASSES.items():
        print(f"  {class_id} - {class_name}: {state.saved_by_class[class_id]}")
    print(f"  Rejeitadas por desfoque: {state.rejected_blurry}")
    print(f"  Saída: {output.resolve()}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        cv2, np = load_vision_modules()
    except RuntimeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    backend = resolve_backend(args.backend)
    args.output.mkdir(parents=True, exist_ok=True)
    state = CaptureState(
        session_id=safe_component(args.session), crop_guide=args.crop_guide
    )
    manifest = ManifestWriter(args.output / "manifest.csv")
    camera = None
    window_name = "Vigi - Coleta Assistida"
    last_burst_capture = 0.0
    last_manual_capture = 0.0
    message = "Posicione a garrafa dentro da guia"
    message_until = time.monotonic() + 3

    try:
        camera = open_camera(args, cv2, np, backend)
        print(f"[OK] Câmera aberta com backend {backend}.")
        print(f"[OK] Sessão: {state.session_id}")
        print("[INFO] Pressione Q ou ESC para encerrar com segurança.")
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        while True:
            ok, frame = camera.read()
            if not ok or frame is None:
                raise RuntimeError("A câmera parou de fornecer imagens.")
            frame_height, frame_width = frame.shape[:2]
            guide = guide_bounds(
                frame_width,
                frame_height,
                args.guide_width,
                args.guide_height,
            )
            score = sharpness_score(cv2, frame)
            now = time.monotonic()
            visible_message = message if now < message_until else ""
            preview = draw_overlay(
                cv2,
                frame,
                state,
                guide,
                score,
                args.blur_threshold,
                visible_message,
            )
            cv2.imshow(window_name, preview)
            key = cv2.waitKey(1) & 0xFF

            selected = class_from_key(key)
            if selected is not None:
                state.select_class(selected)
                message = f"Classe selecionada: {state.class_name}"
                message_until = now + 2
            elif key in (ord("q"), ord("Q"), 27):
                break
            elif key in (ord("b"), ord("B")):
                state.burst_enabled = not state.burst_enabled
                last_burst_capture = 0.0
                message = "Burst ligado" if state.burst_enabled else "Burst desligado"
                message_until = now + 2
            elif key in (ord("n"), ord("N")):
                state.next_physical_sample()
                message = f"Novo frasco físico: {state.physical_sample:03d}"
                message_until = now + 2
            elif key in (ord("c"), ord("C")):
                state.crop_guide = not state.crop_guide
                message = "Recorte da guia ligado" if state.crop_guide else "Quadro inteiro"
                message_until = now + 2

            manual_requested = key == ord(" ") and now - last_manual_capture >= 0.25
            burst_requested = (
                state.burst_enabled
                and now - last_burst_capture >= args.burst_interval
            )
            if manual_requested or burst_requested:
                mode = "manual" if manual_requested else "burst"
                saved = save_capture(
                    cv2,
                    frame,
                    state,
                    args,
                    backend,
                    guide,
                    score,
                    mode,
                    manifest,
                )
                if manual_requested:
                    last_manual_capture = now
                if burst_requested:
                    last_burst_capture = now
                if saved is None:
                    message = f"Descartada: desfocada ({score:.1f})"
                else:
                    message = f"Salva: {saved.name}"
                message_until = now + 1.5
    except KeyboardInterrupt:
        print("\n[INFO] Coleta interrompida pelo usuário.")
    except RuntimeError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    finally:
        state.burst_enabled = False
        if camera is not None:
            camera.release()
        manifest.close()
        cv2.destroyAllWindows()
        print_summary(state, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
