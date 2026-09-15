"""Testes do driver de sinalização física local."""

from unittest.mock import MagicMock

import pytest

from edge.actuation.indicators import (
    GPIOStatusIndicators,
    validate_gpio_pin_assignments,
)


def make_indicators() -> tuple[GPIOStatusIndicators, MagicMock, MagicMock, MagicMock]:
    green_led = MagicMock()
    red_led = MagicMock()
    buzzer = MagicMock()
    indicators = GPIOStatusIndicators(
        green_led=green_led,
        red_led=red_led,
        buzzer=buzzer,
    )
    return indicators, green_led, red_led, buzzer


def test_status_leds_pulse_in_background_without_overlapping() -> None:
    indicators, green_led, red_led, _ = make_indicators()

    indicators.signal_result("CONFORME")
    indicators.signal_result("NAO_CONFORME")

    red_led.off.assert_called_once()
    green_led.blink.assert_called_once_with(
        on_time=0.15,
        off_time=0.0,
        n=1,
        background=True,
    )
    green_led.off.assert_called_once()
    red_led.blink.assert_called_once_with(
        on_time=0.15,
        off_time=0.0,
        n=1,
        background=True,
    )


def test_critical_alarm_beeps_until_acknowledged() -> None:
    indicators, _, _, buzzer = make_indicators()

    indicators.signal_critical_alarm()
    indicators.signal_critical_alarm()

    buzzer.beep.assert_called_once_with(
        on_time=0.25,
        off_time=0.25,
        n=None,
        background=True,
    )

    indicators.acknowledge_alarm()

    buzzer.off.assert_called_once()


def test_close_releases_every_gpio_device() -> None:
    indicators, green_led, red_led, buzzer = make_indicators()

    indicators.close()
    indicators.close()

    green_led.close.assert_called_once()
    red_led.close.assert_called_once()
    buzzer.close.assert_called_once()


def test_gpio_pin_assignments_must_be_unique() -> None:
    with pytest.raises(ValueError, match="GPIO 17.*sensor.*led_vermelho"):
        validate_gpio_pin_assignments(
            sensor=17,
            led_verde=27,
            led_vermelho=17,
            buzzer=23,
        )


def test_gpio_pin_assignments_accept_issue_32_defaults() -> None:
    validate_gpio_pin_assignments(
        sensor=17,
        led_verde=27,
        led_vermelho=22,
        buzzer=23,
    )
