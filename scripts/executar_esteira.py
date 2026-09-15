#!/usr/bin/env python3
"""Executa o laço de inspeção contínua da esteira do Vigi na Raspberry Pi 5.

Integração física do sensor fotoelétrico E18-D80NK (GPIO 17) com a câmera
(Picamera2/CSI), execução da inferência em borda e publicação não-bloqueante no MQTT
com Last Will and Testament (LWT) e alarmes operacionais.
"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.acquisition.camera import Camera  # noqa: E402
from edge.acquisition.sensor import (  # noqa: E402
    PhotoelectricSensor,
    SimulatedPhotoelectricSensor,
)
from edge.actuation.indicators import (  # noqa: E402
    GPIOStatusIndicators,
    validate_gpio_pin_assignments,
)
from edge.inference.engine import InferenceEngine  # noqa: E402
from edge.messaging.context import OperationalContext  # noqa: E402
from edge.messaging.event import InspectionEvent  # noqa: E402
from edge.messaging.publisher import MQTTInspectionPublisher  # noqa: E402
from edge.orchestration.conveyor import ConveyorOrchestrator, CycleTiming  # noqa: E402


def create_camera(
    backend: str,
    camera_id: int,
    width: int,
    height: int,
    warmup_seconds: float = 2.0,
) -> Camera:
    from edge.acquisition.camera import CameraFactory

    resolved_backend = CameraFactory.resolve_backend(backend)
    if resolved_backend == "picamera2":
        from edge.acquisition.backends.picamera2_camera import Picamera2Camera

        return Picamera2Camera(
            device=camera_id,
            width=width,
            height=height,
            fps=20,
            warmup_seconds=warmup_seconds,
        )
    else:
        from edge.acquisition import load_opencv
        from edge.acquisition.backends.opencv_camera import OpenCVCamera

        cv2 = load_opencv()
        return OpenCVCamera(
            cv2=cv2,
            device=camera_id,
            width=width,
            height=height,
            fps=20,
        )



def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa o orquestrador da esteira do Vigi"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("models/active/manifest.json"),
        help="Caminho do manifest do modelo ativo",
    )
    parser.add_argument(
        "--backend",
        choices=("picamera2", "opencv", "auto"),
        default="picamera2",
        help="Backend de captura de câmera",
    )
    parser.add_argument(
        "--camera-id",
        type=int,
        default=0,
        help="Índice do dispositivo de câmera",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1280,
        help="Largura do quadro de captura",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="Altura do quadro de captura",
    )
    parser.add_argument(
        "--gpio-pin",
        type=int,
        default=17,
        help="Pino GPIO da Raspberry Pi conectado ao sensor E18-D80NK",
    )
    parser.add_argument(
        "--debounce-ms",
        type=float,
        default=50.0,
        help="Filtro de debounce em ms (30 a 100 ms, conforme RNF08)",
    )
    parser.add_argument(
        "--enable-indicators",
        action="store_true",
        help="Ativar LEDs e buzzer físicos da issue #32",
    )
    parser.add_argument(
        "--green-led-pin",
        type=int,
        default=27,
        help="GPIO BCM do LED verde (padrão: 27)",
    )
    parser.add_argument(
        "--red-led-pin",
        type=int,
        default=22,
        help="GPIO BCM do LED vermelho (padrão: 22)",
    )
    parser.add_argument(
        "--buzzer-pin",
        type=int,
        default=23,
        help="GPIO BCM do driver do buzzer ativo (padrão: 23)",
    )
    parser.add_argument(
        "--critical-alarm-after",
        type=int,
        default=3,
        help="Não conformidades consecutivas para disparar o buzzer (padrão: 3)",
    )
    parser.add_argument(
        "--mqtt-host",
        default="localhost",
        help="Endereço do broker Mosquitto",
    )
    parser.add_argument(
        "--mqtt-port",
        type=int,
        default=1883,
        help="Porta do broker Mosquitto",
    )
    parser.add_argument(
        "--mqtt-topic",
        default="vigi/esteira/inspecoes",
        help="Tópico MQTT de eventos de inspeção",
    )
    parser.add_argument(
        "--mqtt-alarms",
        default="vigi/esteira/alarmes",
        help="Tópico MQTT de alarmes operacionais",
    )
    parser.add_argument(
        "--mqtt-status",
        default="vigi/esteira/status",
        help="Tópico MQTT de status e LWT do nó de borda",
    )
    parser.add_argument(
        "--station-code",
        default="ESTACAO_01",
        help="Código da estação operacional vinculada",
    )
    parser.add_argument(
        "--batch-code",
        default="LOTE_01",
        help="Código do lote ativo para rastreabilidade",
    )
    parser.add_argument(
        "--max-inspections",
        type=int,
        default=None,
        help="Encerrar após N inspeções (padrão: contínuo)",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path("captures"),
        help="Diretório onde salvar as fotos das inspeções (padrão: captures/)",
    )
    parser.add_argument(
        "--simulated-sensor",
        action="store_true",
        help="Usar sensor simulado por software",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Sobrescrever limiar de confianca da inferencia (ex: 0.70)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ativar logs detalhados de debug",
    )
    return parser.parse_args(argv)


def validate_hardware_pin_configuration(args: argparse.Namespace) -> None:
    """Rejeita configurações que disputem uma GPIO física."""
    if not args.enable_indicators:
        return
    if args.critical_alarm_after < 1:
        raise ValueError("critical_alarm_after deve ser maior ou igual a 1")

    assignments = {
        "led_verde": args.green_led_pin,
        "led_vermelho": args.red_led_pin,
        "buzzer": args.buzzer_pin,
    }
    if not args.simulated_sensor:
        assignments["sensor"] = args.gpio_pin
    validate_gpio_pin_assignments(**assignments)


def format_inspection_banner(event: InspectionEvent, timing: CycleTiming) -> str:
    """Formata um bloco visual destacado com o resultado e tipo de não conformidade."""
    conf_str = (
        f"{event.confidence * 100:.1f}%" if event.confidence is not None else "N/A"
    )
    lat_status = "ATENDIDO" if timing.total_ms < 500.0 else "EXCEDIDO"
    lines = [
        "",
        "=" * 64,
    ]
    if event.result == "CONFORME":
        lines.append(f"  ✅ [INSPEÇÃO #{event.inspection_id}] STATUS: CONFORME")
        lines.append(
            f"     Confiança: {conf_str} | Latência: {timing.total_ms:.1f} ms "
            f"[RNF01 {lat_status}]"
        )
    else:
        if event.nonconformity_type:
            defect_desc = f"ANOMALIA NO PRODUTO: {event.nonconformity_type}"
        elif event.technical_failure_type:
            defect_desc = f"FALHA TÉCNICA: {event.technical_failure_type}"
        else:
            defect_desc = "DEFEITO NÃO ESPECIFICADO"

        lines.append(f"  ❌ [INSPEÇÃO #{event.inspection_id}] STATUS: NÃO CONFORME")
        lines.append(f"     🔴 Motivo / Defeito: {defect_desc}")
        lines.append(
            f"     Confiança: {conf_str} | Latência: {timing.total_ms:.1f} ms "
            f"[RNF01 {lat_status}]"
        )
        lines.append(
            "     🚨 Alarme operacional emitido no MQTT ('vigi/esteira/alarmes')"
        )
    lines.append("=" * 64)
    return "\n".join(lines)



def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose)
    logger = logging.getLogger("vigi.conveyor")

    try:
        validate_hardware_pin_configuration(args)
    except ValueError as exc:
        logger.error("Configuração de GPIO inválida: %s", exc)
        return 2

    logger.info("=" * 60)
    logger.info("VIGI — SISTEMA EMBARCADO DE INSPEÇÃO EM ESTEIRA (RPi 5)")
    logger.info("=" * 60)

    # 1. Carregamento do Modelo de Inferência
    if not args.manifest.is_file():
        logger.error(
            "Manifesto do modelo ativo não encontrado em '%s'. "
            "Execute 'python scripts/promover_modelo.py' antes de iniciar a esteira.",
            args.manifest,
        )
        return 1

    try:
        engine = InferenceEngine.from_manifest(args.manifest)
        if args.threshold is not None:
            engine.threshold = args.threshold
            logger.info(
                "Limiar de confiança ajustado via CLI: %.2f (manifesto original: %.2f)",
                args.threshold,
                engine.manifest.confidence_threshold,
            )
        else:
            logger.info(
                "Limiar de confiança ativo: %.2f (do manifesto)",
                engine.threshold,
            )
        logger.info("Modelo carregado com sucesso via %s", args.manifest)
    except Exception as exc:
        logger.error("Falha ao inicializar o motor de inferência: %s", exc)
        return 1

    # 2. Inicialização da Câmera (mantida aberta em streaming)
    try:
        camera = create_camera(
            backend=args.backend,
            camera_id=args.camera_id,
            width=args.width,
            height=args.height,
            warmup_seconds=2.0,
        )
        logger.info(
            "Câmera '%s' inicializada e aquecida (pronta para disparo)", args.backend
        )
    except Exception as exc:
        logger.error("Falha ao inicializar a câmera: %s", exc)
        return 1

    # 3. Inicialização do Sensor E18-D80NK
    if args.simulated_sensor:
        sensor = SimulatedPhotoelectricSensor(debounce_ms=args.debounce_ms)
        logger.info("Sensor SIMULADO inicializado.")
    else:
        try:
            sensor = PhotoelectricSensor(
                pin=args.gpio_pin,
                debounce_ms=args.debounce_ms,
                pull_up=True,
            )
            logger.info(
                "Sensor fotoelétrico E18-D80NK ativo na GPIO %d (debounce=%.1f ms)",
                args.gpio_pin,
                args.debounce_ms,
            )
        except Exception as exc:
            logger.error(
                "Falha ao inicializar o sensor na GPIO %d: %s", args.gpio_pin, exc
            )
            camera.release()
            return 1

    # 4. Sinalização física opcional
    indicators = None
    if args.enable_indicators:
        try:
            indicators = GPIOStatusIndicators(
                green_pin=args.green_led_pin,
                red_pin=args.red_led_pin,
                buzzer_pin=args.buzzer_pin,
            )
            logger.info(
                "Indicadores ativos: verde=GPIO%d, vermelho=GPIO%d, buzzer=GPIO%d",
                args.green_led_pin,
                args.red_led_pin,
                args.buzzer_pin,
            )
        except Exception as exc:
            logger.error("Falha ao inicializar os indicadores GPIO: %s", exc)
            sensor.close()
            camera.release()
            return 1

    # 5. Contexto operacional e publicador MQTT com LWT
    context = None
    if args.station_code and args.batch_code:
        context = OperationalContext(
            station_code=args.station_code, batch_code=args.batch_code
        )

    topic = (
        context.inspections_topic
        if (context and args.mqtt_topic == "vigi/esteira/inspecoes")
        else args.mqtt_topic
    )
    publisher = MQTTInspectionPublisher(
        host=args.mqtt_host,
        port=args.mqtt_port,
        topic=topic,
        topic_alarms=args.mqtt_alarms,
        topic_status=args.mqtt_status,
        client_id="vigi-edge-gateway-rpi5",
    )

    def handle_inspection(event: InspectionEvent, timing: CycleTiming) -> None:
        logger.info(format_inspection_banner(event, timing))

    orchestrator = ConveyorOrchestrator(
        sensor=sensor,
        camera=camera,
        engine=engine,
        publisher=publisher,
        context=context,
        save_dir=args.save_dir,
        on_inspection=handle_inspection,
        indicators=indicators,
        critical_alarm_after=args.critical_alarm_after,
    )


    # Tratamento de interrupção suave (Ctrl+C / SIGINT / SIGTERM)
    def signal_handler(signum, frame):
        logger.info("Sinal %d recebido. Finalizando esteira...", signum)
        orchestrator.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if indicators is not None and hasattr(signal, "SIGUSR1"):

        def acknowledge_alarm_handler(signum, frame):
            logger.info("Reconhecimento do alarme físico recebido.")
            orchestrator.acknowledge_alarm()

        signal.signal(signal.SIGUSR1, acknowledge_alarm_handler)
        logger.info(
            "Para reconhecer e silenciar o buzzer: kill -USR1 %d", os.getpid()
        )

    try:
        orchestrator.run(max_cycles=args.max_inspections)
    except Exception as exc:
        logger.error("Erro inesperado no laço da esteira: %s", exc, exc_info=True)
        return 1

    logger.info(
        "Execução finalizada com sucesso. Total de frascos inspecionados: %d",
        orchestrator.inspections_count,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
