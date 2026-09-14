#!/usr/bin/env python3
"""Servidor HTTP de preview da câmera ao vivo para ajuste de enquadramento."""

from __future__ import annotations

import argparse
import logging
import socket
import sys
from http import server
from pathlib import Path
from socketserver import ThreadingMixIn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.acquisition import load_opencv  # noqa: E402
from scripts.executar_esteira import create_camera  # noqa: E402

logger = logging.getLogger("vigi.preview")

PAGE_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vigi — Preview de Enquadramento</title>
    <style>
        body {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #58a6ff; margin-bottom: 6px; }
        p { color: #8b949e; margin-top: 0; margin-bottom: 20px; font-size: 15px; }
        .container {
            display: inline-block;
            background: #161b22;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #30363d;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        img {
            max-width: 95vw;
            max-height: 75vh;
            border-radius: 8px;
            border: 2px solid #238636;
            display: block;
        }
        .guide {
            margin-top: 15px;
            font-size: 13px;
            color: #7ee787;
        }
    </style>
</head>
<body>
    <h1>VIGI — Enquadramento e Foco da Câmera</h1>
    <p>Ajuste o plano focal e o sensor E18-D80NK na esteira.</p>
    <div class="container">
        <img src="/stream.mjpg" alt="Transmissão ao vivo da câmera da esteira" />
        <div class="guide">Guia central verde: Região ideal de passagem do frasco</div>
    </div>
</body>
</html>
"""


class StreamingServer(ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def make_handler(camera, cv2):
    class StreamingHandler(server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(PAGE_HTML.encode("utf-8"))
            elif self.path == "/stream.mjpg":
                self.send_response(200)
                self.send_header("Age", "0")
                self.send_header("Cache-Control", "no-cache, private")
                self.send_header("Pragma", "no-cache")
                self.send_header(
                    "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
                )
                self.end_headers()
                try:
                    while True:
                        ok, frame = camera.read()
                        if not ok or frame is None:
                            continue

                        # Converte RGB para BGR para OpenCV
                        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        h, w = bgr.shape[:2]

                        # Desenha guia central de enquadramento
                        gw = int(w * 0.45)
                        gh = int(h * 0.75)
                        x1 = (w - gw) // 2
                        y1 = (h - gh) // 2
                        x2 = x1 + gw
                        y2 = y1 + gh

                        cv2.rectangle(bgr, (x1, y1), (x2, y2), (0, 255, 120), 2)
                        cv2.putText(
                            bgr,
                            "ZONA DE INSPETORIA",
                            (x1 + 10, y1 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 120),
                            2,
                        )

                        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
                        _, jpeg = cv2.imencode(".jpg", bgr, encode_params)
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(jpeg)))
                        self.end_headers()
                        self.wfile.write(jpeg.tobytes())
                        self.wfile.write(b"\r\n")
                except Exception:
                    pass
            else:
                self.send_error(404)
                self.end_headers()

        def log_message(self, format: str, *args) -> None:
            # Silencia logs repetitivos de requisições HTTP
            return

    return StreamingHandler


def detect_host_ip() -> str:
    """Tenta detectar o IP da interface de rede local ativa sem resolver loopback."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    finally:
        s.close()
    return "<IP_DA_RASPBERRY>"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        choices=("picamera2", "opencv"),
        default="picamera2",
        help="Backend de câmera",
    )
    parser.add_argument("--camera-id", type=int, default=0)
    parser.add_argument(
        "--port", type=int, default=8080, help="Porta HTTP do servidor"
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    cv2 = load_opencv()
    logger.info("Inicializando câmera '%s'...", args.backend)
    camera = create_camera(
        backend=args.backend,
        camera_id=args.camera_id,
        width=args.width,
        height=args.height,
        warmup_seconds=1.5,
    )

    handler_class = make_handler(camera, cv2)
    address = ("", args.port)
    httpd = StreamingServer(address, handler_class)

    host_ip = detect_host_ip()
    logger.info("=" * 60)
    logger.info("PREVIEW AO VIVO DA CÂMERA INICIADO!")
    logger.info("Abra no navegador do seu notebook:")
    logger.info("👉 http://%s:%d", host_ip, args.port)
    logger.info("Pressione Ctrl+C para encerrar o preview.")
    logger.info("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nEncerrando servidor de preview...")
    finally:
        httpd.server_close()
        camera.release()
        logger.info("Câmera liberada.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
