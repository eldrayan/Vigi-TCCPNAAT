"""Testes das opções de hardware da CLI da esteira."""

import pytest

from scripts.executar_esteira import parse_args, validate_hardware_pin_configuration


def test_indicator_gpio_defaults_do_not_conflict_with_sensor() -> None:
    args = parse_args(["--enable-indicators"])

    validate_hardware_pin_configuration(args)

    assert args.gpio_pin == 17
    assert args.green_led_pin == 27
    assert args.red_led_pin == 22
    assert args.buzzer_pin == 23
    assert args.critical_alarm_after == 3


def test_indicator_gpio_collision_with_sensor_is_rejected() -> None:
    args = parse_args(["--enable-indicators", "--red-led-pin", "17"])

    with pytest.raises(ValueError, match="GPIO 17.*sensor.*led_vermelho"):
        validate_hardware_pin_configuration(args)


def test_indicator_gpio_pins_are_ignored_when_feature_is_disabled() -> None:
    args = parse_args(["--red-led-pin", "17"])

    validate_hardware_pin_configuration(args)

    assert not args.enable_indicators


def test_critical_alarm_limit_must_be_positive() -> None:
    args = parse_args(["--enable-indicators", "--critical-alarm-after", "0"])

    with pytest.raises(ValueError, match="maior ou igual a 1"):
        validate_hardware_pin_configuration(args)
