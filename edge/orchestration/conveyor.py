"""Orquestrador ponta a ponta da esteira de inspeção do Vigi.

Integração de Hardware (Sensor E18-D80NK + Câmera + Edge AI + Gateway MQTT).
Atende a:
- RN01: Inspeção automatizada por gatilho determinístico de presença.
- RN02: Ação preventiva de Fail-Safe em caso de baixa confiança ou erro técnico.
- RNF01: Latência total ponta a ponta < 500 ms.
- RNF04: Telemetria MQTT não-bloqueante, reconexão e LWT.
- RNF08: Sensor fotoelétrico com filtro de debounce de 30 a 100 ms.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from edge.acquisition.camera import Camera
from edge.acquisition.sensor import PhotoelectricSensor, SensorTrigger
from edge.actuation.indicators import StatusIndicators
from edge.inference.engine import InferenceEngine
from edge.inference.schemas import InspectionDecision
from edge.messaging.context import OperationalContext
from edge.messaging.event import InspectionEvent
from edge.messaging.publisher import MQTTInspectionPublisher

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CycleTiming:
    capture_ms: float
    inference_ms: float
    publish_ms: float
    total_ms: float


class ConveyorOrchestrator:
    """Orquestrador de execução contínua da esteira de inspeção."""

    def __init__(
        self,
        sensor: SensorTrigger | PhotoelectricSensor,
        camera: Camera,
        engine: InferenceEngine,
        publisher: MQTTInspectionPublisher,
        *,
        context: OperationalContext | None = None,
        on_inspection: Callable[[InspectionEvent, CycleTiming], None] | None = None,
        save_dir: Path | None = None,
        indicators: StatusIndicators | None = None,
        critical_alarm_after: int = 3,
    ) -> None:
        if critical_alarm_after < 1:
            raise ValueError("critical_alarm_after deve ser maior ou igual a 1")
        self.sensor = sensor
        self.camera = camera
        self.engine = engine
        self.publisher = publisher
        self.context = context
        self.on_inspection = on_inspection
        self.save_dir = save_dir
        self.indicators = indicators
        self.critical_alarm_after = critical_alarm_after
        self._stop_event = threading.Event()
        self._inspections_count = 0
        self._consecutive_nonconformities = 0

    @property
    def inspections_count(self) -> int:
        return self._inspections_count

    def process_cycle(self) -> tuple[InspectionEvent, CycleTiming]:
        """Executa um ciclo completo de captura, inferência e publicação."""
        t_start = time.perf_counter()

        # 1. Aquisição imediata do quadro focal
        ok, frame = self.camera.read()
        t_captured = time.perf_counter()
        if not ok or frame is None:
            raise RuntimeError(
                "Câmera falhou ao fornecer o quadro no momento do disparo."
            )

        capture_ms = (t_captured - t_start) * 1000.0

        # 2. Inferência Edge AI
        decision = self.engine.inspect(frame)
        t_inferred = time.perf_counter()
        inference_ms = (t_inferred - t_captured) * 1000.0

        # 3. Composição e Publicação MQTT
        event = InspectionEvent.from_decision(decision, context=self.context)
        self.publisher.publish_inspection(event)

        # 4. Alarme para não-conformidades ou falhas técnicas (RN02 / RNF04)
        if decision.result != "CONFORME" or decision.technical_failure_type is not None:
            alert_name = (
                decision.technical_failure_type
                or decision.nonconformity_type
                or "ALERTA"
            )
            alarm_payload = {
                "inspection_id": event.inspection_id,
                "timestamp": event.timestamp,
                "alert_type": alert_name,
                "severity": "CRITICAL"
                if decision.technical_failure_type
                else "WARNING",
                "message": f"Não conformidade detectada: {alert_name}",
            }
            self.publisher.publish_alarm(alarm_payload)

        self._update_indicators(decision)

        t_end = time.perf_counter()
        publish_ms = (t_end - t_inferred) * 1000.0
        total_ms = (t_end - t_start) * 1000.0

        timing = CycleTiming(
            capture_ms=capture_ms,
            inference_ms=inference_ms,
            publish_ms=publish_ms,
            total_ms=total_ms,
        )

        self._inspections_count += 1

        if self.save_dir is not None:
            try:
                import cv2

                self.save_dir.mkdir(parents=True, exist_ok=True)
                bgr = (
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    if (frame.ndim == 3 and frame.shape[2] == 3)
                    else frame
                )
                cv2.imwrite(str(self.save_dir / "ultima_inspecao.jpg"), bgr)
                cv2.imwrite(
                    str(
                        self.save_dir
                        / f"inspecao_{event.inspection_id}_{event.result}.jpg"
                    ),
                    bgr,
                )
            except Exception as exc:
                logger.warning("Falha ao salvar imagem de inspeção: %s", exc)

        if self.on_inspection is not None:
            self.on_inspection(event, timing)

        return event, timing

    def _update_indicators(self, decision: InspectionDecision) -> None:
        if decision.result == "CONFORME":
            self._consecutive_nonconformities = 0
        else:
            self._consecutive_nonconformities += 1

        if self.indicators is None:
            return

        try:
            self.indicators.signal_result(decision.result)
        except Exception as exc:
            logger.warning("Falha na sinalização visual local: %s", exc)

        is_critical = (
            decision.technical_failure_type is not None
            or self._consecutive_nonconformities == self.critical_alarm_after
        )
        if is_critical:
            self.trigger_critical_alarm()

    def trigger_critical_alarm(self) -> None:
        """Dispara o alarme físico para uma regra crítica interna ou externa."""
        if self.indicators is None:
            return
        try:
            self.indicators.signal_critical_alarm()
        except Exception as exc:
            logger.warning("Falha na sinalização sonora local: %s", exc)

    def acknowledge_alarm(self) -> None:
        """Silencia um alarme físico após reconhecimento externo do operador."""
        if self.indicators is None:
            return
        try:
            self.indicators.acknowledge_alarm()
            self._consecutive_nonconformities = 0
        except Exception as exc:
            logger.warning("Falha ao reconhecer alarme físico: %s", exc)

    def run(
        self,
        max_cycles: int | None = None,
        poll_interval: float = 0.05,
    ) -> None:
        """Inicia o laço de supervisão contínua da esteira."""
        logger.info(
            "Iniciando orquestração da esteira (aguardando frascos via sensor)..."
        )
        self.publisher.start_session()

        try:
            while not self._stop_event.is_set():
                if max_cycles is not None and self._inspections_count >= max_cycles:
                    logger.info(
                        "Limite de %d ciclos atingido. Encerrando loop.", max_cycles
                    )
                    break

                # Aguarda o sensor disparar
                triggered = self.sensor.wait_for_trigger(timeout=poll_interval)
                if self._stop_event.is_set():
                    break
                if not triggered:
                    continue

                logger.debug("Gatilho fotoelétrico detectado! Processando frasco...")
                try:
                    event, timing = self.process_cycle()
                    logger.info(
                        "Inspeção #%d concluída: %s (%s) em %.1f ms [RNF01 %s]",
                        event.inspection_id,
                        event.result,
                        event.nonconformity_type
                        or event.technical_failure_type
                        or "OK",
                        timing.total_ms,
                        "ATENDIDO" if timing.total_ms < 500.0 else "EXCEDIDO",
                    )
                except Exception as exc:
                    logger.error(
                        "Erro ao processar ciclo de inspeção: %s", exc, exc_info=True
                    )
        finally:
            self.stop()

    def stop(self) -> None:
        """Interrompe a execução e libera recursos."""
        self._stop_event.set()
        self.publisher.stop_session()
        self.sensor.close()
        self.camera.release()
        if self.indicators is not None:
            self.indicators.close()
        logger.info("Orquestrador da esteira finalizado.")
