"""
Descrição: Orquestra o ciclo ponta a ponta da esteira de inspeção.
Autor: Leôncio Ferreira
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
from edge.inference.engine import InferenceEngine
from edge.messaging.context import OperationalContext
from edge.messaging.event import InspectionEvent
from edge.messaging.outbox import InspectionOutbox
from edge.messaging.publisher import MQTTInspectionPublisher

from .capture_store import InspectionCaptureStore
from .inspection_dispatcher import InspectionDispatcher

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CycleTiming:
    capture_ms: float
    inference_ms: float
    publish_ms: float
    total_ms: float


class ConveyorOrchestrator:
    def __init__(
        self,
        sensor: SensorTrigger | PhotoelectricSensor,
        camera: Camera,
        engine: InferenceEngine,
        publisher: MQTTInspectionPublisher,
        *,
        outbox: InspectionOutbox | None = None,
        context: OperationalContext | None = None,
        on_inspection: Callable[[InspectionEvent, CycleTiming], None] | None = None,
        on_idle: Callable[[bool], None] | None = None,
        save_dir: Path | None = None,
        capture_delay_s: float = 0.0,
    ) -> None:
        self.sensor = sensor
        self.camera = camera
        self.engine = engine
        self.publisher = publisher
        self.dispatcher = InspectionDispatcher(publisher, outbox)
        self.context = context
        self.on_inspection = on_inspection
        self.on_idle = on_idle
        self.capture_store = InspectionCaptureStore(save_dir) if save_dir else None
        self.capture_delay_s = capture_delay_s
        self._stop_event = threading.Event()
        self._inspections_count = 0
        self._idle_state: bool | None = None

    @property
    def inspections_count(self) -> int:
        return self._inspections_count

    def process_cycle(self) -> tuple[InspectionEvent, CycleTiming]:
        t_start = time.perf_counter()

        if self.capture_delay_s > 0:
            time.sleep(self.capture_delay_s)

        ok, frame = self.camera.read()
        t_captured = time.perf_counter()
        if not ok or frame is None:
            raise RuntimeError(
                "Câmera falhou ao fornecer o quadro no momento do disparo."
            )

        capture_ms = (t_captured - t_start) * 1000.0

        decision = self.engine.inspect(frame)
        t_inferred = time.perf_counter()
        inference_ms = (t_inferred - t_captured) * 1000.0

        event = self.dispatcher.dispatch(decision, self.context)

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

        if self.capture_store is not None:
            try:
                self.capture_store.save(
                    frame,
                    inspection_id=event.inspection_id,
                    result=event.result,
                )
            except Exception as exc:
                logger.warning("Falha ao salvar imagem de inspeção: %s", exc)

        if self.on_inspection is not None:
            self.on_inspection(event, timing)

        return event, timing

    def run(
        self,
        max_cycles: int | None = None,
        poll_interval: float = 0.05,
    ) -> None:
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

                triggered = self.sensor.wait_for_trigger(timeout=poll_interval)
                if self._stop_event.is_set():
                    break
                if not triggered:
                    self._set_idle(True)
                    continue

                self._set_idle(False)
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

    def _set_idle(self, is_idle: bool) -> None:
        if self._idle_state == is_idle:
            return
        self._idle_state = is_idle
        if self.on_idle is not None:
            self.on_idle(is_idle)

    def stop(self) -> None:
        self._stop_event.set()
        self.publisher.stop_session()
        self.sensor.close()
        self.camera.release()
        logger.info("Orquestrador da esteira finalizado.")
