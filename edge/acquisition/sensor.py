"""Interface e controle do sensor fotoelétrico infravermelho E18-D80NK via GPIO."""

from __future__ import annotations

import logging
import queue
import threading
import time
from collections.abc import Callable
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class SensorTrigger(Protocol):
    """Protocolo base para sensores de presença com disparo por gatilho."""

    def wait_for_trigger(self, timeout: float | None = None) -> bool:
        """Aguarda a detecção física do frasco, retornando True se acionado."""
        ...

    def close(self) -> None:
        """Libera os recursos do sensor."""
        ...


class PhotoelectricSensor:
    """Controlador do sensor fotoelétrico infravermelho E18-D80NK.

    Implementa leitura digital via interrupção de GPIO com filtro de debounce
    entre 30 ms e 100 ms (RNF08), tratando a saída digital NPN (nível lógico
    baixo ativo na presença do recipiente).
    """

    def __init__(
        self,
        pin: int = 17,
        debounce_ms: float = 50.0,
        pull_up: bool = True,
        rearm_delay_s: float = 0.2,
        gpio_device: Any | None = None,
    ) -> None:
        if not (30.0 <= debounce_ms <= 100.0):
            raise ValueError(
                "debounce_ms deve estar entre 30 e 100 ms (RNF08), "
                f"recebido: {debounce_ms}"
            )

        self.pin = pin
        self.debounce_s = debounce_ms / 1000.0
        self.rearm_delay_s = rearm_delay_s
        self._trigger_event = threading.Event()
        self._callback: Callable[[], None] | None = None
        self._last_trigger_time = 0.0
        self._closed = False

        if gpio_device is not None:
            self._device = gpio_device
            self._setup_events()
        else:
            try:
                from gpiozero import DigitalInputDevice

                # No E18-D80NK NPN:
                # Nível 1 (alto) em repouso
                # Nível 0 (baixo) quando detecta objeto -> active_state=False
                self._device = DigitalInputDevice(
                    pin=pin,
                    pull_up=None,
                    active_state=False,
                    bounce_time=self.debounce_s,
                )
                self._setup_events()
            except Exception as exc:
                logger.warning(
                    "Não foi possível inicializar gpiozero na GPIO %d: %s. "
                    "Operando em modo stub.",
                    pin,
                    exc,
                )
                self._device = None

    def _setup_events(self) -> None:
        if self._device is None:
            return

        if hasattr(self._device, "when_activated"):
            self._device.when_activated = self._on_falling_edge

    def _on_falling_edge(self) -> None:
        """Callback acionado na transição de detecção de presença."""
        if self._closed:
            return

        now = time.monotonic()
        # Lockout para evitar re-gatilho no mesmo frasco
        if (now - self._last_trigger_time) < self.rearm_delay_s:
            return

        self._last_trigger_time = now
        self._trigger_event.set()

        if self._callback is not None:
            try:
                self._callback()
            except Exception as exc:
                logger.error("Erro no callback do sensor: %s", exc)

    @property
    def when_trigger(self) -> Callable[[], None] | None:
        return self._callback

    @when_trigger.setter
    def when_trigger(self, callback: Callable[[], None] | None) -> None:
        self._callback = callback

    @property
    def is_detected(self) -> bool:
        """Retorna True se há um frasco atualmente em frente ao sensor."""
        if self._device is None:
            return False
        return bool(self._device.is_active)

    def wait_for_trigger(self, timeout: float | None = None) -> bool:
        """Bloqueia até o sensor detectar um frasco ou o timeout expirar."""
        triggered = self._trigger_event.wait(timeout=timeout)
        if triggered:
            self._trigger_event.clear()
        return triggered

    def trigger(self) -> None:
        """Disparo manual / sintético para testes e simulação."""
        self._on_falling_edge()

    def close(self) -> None:
        """Encerra a leitura da GPIO e libera pinos."""
        self._closed = True
        self._trigger_event.set()
        if self._device is not None and hasattr(self._device, "close"):
            self._device.close()
            self._device = None


class SimulatedPhotoelectricSensor:
    """Sensor fotoelétrico simulado para testes e ambiente sem hardware."""

    def __init__(self, debounce_ms: float = 50.0) -> None:
        self.debounce_ms = debounce_ms
        self._queue: queue.Queue[bool] = queue.Queue()
        self._callback: Callable[[], None] | None = None
        self._closed = False

    def trigger(self) -> None:
        if self._closed:
            return
        self._queue.put(True)
        if self._callback:
            self._callback()

    @property
    def when_trigger(self) -> Callable[[], None] | None:
        return self._callback

    @when_trigger.setter
    def when_trigger(self, callback: Callable[[], None] | None) -> None:
        self._callback = callback

    def wait_for_trigger(self, timeout: float | None = None) -> bool:
        if self._closed:
            return False
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return False

    def close(self) -> None:
        self._closed = True
        self._queue.put(False)
