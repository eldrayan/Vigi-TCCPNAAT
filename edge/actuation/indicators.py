"""Sinalização local com LEDs de status e buzzer ativo via GPIO Zero."""

from __future__ import annotations

import logging
import threading
from typing import Protocol

logger = logging.getLogger(__name__)


class _StatusLight(Protocol):
    def blink(
        self,
        on_time: float,
        off_time: float,
        n: int | None,
        background: bool,
    ) -> None: ...

    def off(self) -> None: ...

    def close(self) -> None: ...


class _AlarmBuzzer(Protocol):
    def beep(
        self,
        on_time: float,
        off_time: float,
        n: int | None,
        background: bool,
    ) -> None: ...

    def off(self) -> None: ...

    def close(self) -> None: ...


class StatusIndicators(Protocol):
    """Contrato dos atuadores usados pelo orquestrador da esteira."""

    def signal_result(self, result: str) -> None:
        """Emite um pulso visual para o resultado da inspeção."""
        ...

    def signal_critical_alarm(self) -> None:
        """Inicia o alarme sonoro intermitente até reconhecimento."""
        ...

    def acknowledge_alarm(self) -> None:
        """Reconhece e silencia o alarme crítico atual."""
        ...

    def close(self) -> None:
        """Desliga e libera os dispositivos GPIO."""
        ...


def validate_gpio_pin_assignments(**assignments: int) -> None:
    """Valida pinos BCM do conector de 40 pinos e detecta sobreposições."""
    owners_by_pin: dict[int, list[str]] = {}
    for owner, pin in assignments.items():
        if not 0 <= pin <= 27:
            raise ValueError(f"GPIO inválida para {owner}: {pin}; use BCM 0 a 27")
        owners_by_pin.setdefault(pin, []).append(owner)

    conflicts = {
        pin: owners for pin, owners in owners_by_pin.items() if len(owners) > 1
    }
    if conflicts:
        details = "; ".join(
            f"GPIO {pin} atribuída a "
            f"{', '.join(sorted(owners, key=lambda owner: (owner != 'sensor', owner)))}"
            for pin, owners in sorted(conflicts.items())
        )
        raise ValueError(f"Conflito de pinagem: {details}")


class GPIOStatusIndicators:
    """Controla os indicadores físicos sem bloquear o ciclo de inspeção.

    ``gpiozero`` executa ``blink`` e ``beep`` em threads de fundo quando
    ``background=True``. Dispositivos podem ser injetados para testes sem GPIO.
    """

    def __init__(
        self,
        green_pin: int = 27,
        red_pin: int = 22,
        buzzer_pin: int = 23,
        *,
        green_led: _StatusLight | None = None,
        red_led: _StatusLight | None = None,
        buzzer: _AlarmBuzzer | None = None,
    ) -> None:
        validate_gpio_pin_assignments(
            led_verde=green_pin,
            led_vermelho=red_pin,
            buzzer=buzzer_pin,
        )

        if green_led is None or red_led is None or buzzer is None:
            from gpiozero import LED, Buzzer

            green_led = LED(green_pin) if green_led is None else green_led
            red_led = LED(red_pin) if red_led is None else red_led
            buzzer = Buzzer(buzzer_pin) if buzzer is None else buzzer

        self._green_led = green_led
        self._red_led = red_led
        self._buzzer = buzzer
        self._alarm_active = False
        self._closed = False
        self._lock = threading.RLock()

    def signal_result(self, result: str) -> None:
        with self._lock:
            if self._closed:
                return
            if result == "CONFORME":
                self._red_led.off()
                self._green_led.blink(
                    on_time=0.15,
                    off_time=0.0,
                    n=1,
                    background=True,
                )
            elif result == "NAO_CONFORME":
                self._green_led.off()
                self._red_led.blink(
                    on_time=0.15,
                    off_time=0.0,
                    n=1,
                    background=True,
                )
            else:
                raise ValueError(f"Resultado de inspeção desconhecido: {result}")

    def signal_critical_alarm(self) -> None:
        with self._lock:
            if self._closed or self._alarm_active:
                return
            self._buzzer.beep(
                on_time=0.25,
                off_time=0.25,
                n=None,
                background=True,
            )
            self._alarm_active = True

    def acknowledge_alarm(self) -> None:
        with self._lock:
            if self._closed or not self._alarm_active:
                return
            self._buzzer.off()
            self._alarm_active = False

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for device in (self._green_led, self._red_led, self._buzzer):
                try:
                    device.off()
                except Exception as exc:
                    logger.warning("Falha ao desligar indicador GPIO: %s", exc)
                try:
                    device.close()
                except Exception as exc:
                    logger.warning("Falha ao liberar indicador GPIO: %s", exc)
