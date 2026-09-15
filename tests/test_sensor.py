"""Testes unitários do driver do sensor fotoelétrico E18-D80NK."""

import time

import pytest

from edge.acquisition.sensor import PhotoelectricSensor, SimulatedPhotoelectricSensor


class MockGPIODevice:
    def __init__(self, initial_value: int = 0) -> None:
        self.value = initial_value
        self.is_active = False
        self.when_deactivated = None
        self.when_activated = None
        self.closed = False

    def simulate_bottle_presence(self) -> None:
        """Simula a passagem do frasco (transição para ativo)."""
        self.value = 1
        self.is_active = True
        if self.when_activated:
            self.when_activated()

    def simulate_bottle_clear(self) -> None:
        self.value = 0
        self.is_active = False
        if self.when_deactivated:
            self.when_deactivated()

    def close(self) -> None:
        self.closed = True


def test_debounce_range_validation() -> None:
    # RNF08: debounce deve estar entre 30 e 100 ms
    PhotoelectricSensor(pin=17, debounce_ms=30.0, gpio_device=MockGPIODevice())
    PhotoelectricSensor(pin=17, debounce_ms=50.0, gpio_device=MockGPIODevice())
    PhotoelectricSensor(pin=17, debounce_ms=100.0, gpio_device=MockGPIODevice())

    with pytest.raises(ValueError, match="RNF08"):
        PhotoelectricSensor(pin=17, debounce_ms=29.0, gpio_device=MockGPIODevice())

    with pytest.raises(ValueError, match="RNF08"):
        PhotoelectricSensor(pin=17, debounce_ms=101.0, gpio_device=MockGPIODevice())


def test_sensor_detects_falling_edge_trigger() -> None:
    mock_gpio = MockGPIODevice(initial_value=1)
    sensor = PhotoelectricSensor(pin=17, debounce_ms=50.0, gpio_device=mock_gpio)

    triggered_events = []
    sensor.when_trigger = lambda: triggered_events.append(time.monotonic())

    # Em repouso
    assert not sensor.is_detected

    # Frasco passa na frente do sensor
    mock_gpio.simulate_bottle_presence()
    assert sensor.is_detected
    assert len(triggered_events) == 1

    # wait_for_trigger deve retornar True imediatamente porque já houve evento
    assert sensor.wait_for_trigger(timeout=0.1)


def test_sensor_rearm_lockout_prevents_multiple_triggers() -> None:
    mock_gpio = MockGPIODevice(initial_value=1)
    sensor = PhotoelectricSensor(
        pin=17,
        debounce_ms=50.0,
        rearm_delay_s=0.2,
        gpio_device=mock_gpio,
    )

    triggered_count = 0

    def on_trigger() -> None:
        nonlocal triggered_count
        triggered_count += 1

    sensor.when_trigger = on_trigger

    # Primeiro disparo
    mock_gpio.simulate_bottle_presence()
    assert triggered_count == 1

    # Disparo repetido antes do rearm_delay (deve ser ignorado)
    mock_gpio.simulate_bottle_presence()
    assert triggered_count == 1

    # Após o tempo de rearmamento
    time.sleep(0.22)
    mock_gpio.simulate_bottle_presence()
    assert triggered_count == 2


def test_simulated_photoelectric_sensor() -> None:
    sim_sensor = SimulatedPhotoelectricSensor(debounce_ms=50.0)
    triggered = []
    sim_sensor.when_trigger = lambda: triggered.append(True)

    sim_sensor.trigger()
    assert len(triggered) == 1
    assert sim_sensor.wait_for_trigger(timeout=0.1)

    sim_sensor.close()


def test_sensor_close_unblocks_and_returns_false() -> None:
    mock_gpio = MockGPIODevice(initial_value=1)
    sensor = PhotoelectricSensor(pin=17, debounce_ms=50.0, gpio_device=mock_gpio)

    # Ao fechar o sensor, qualquer espera deve retornar False
    sensor.close()
    assert not sensor.wait_for_trigger(timeout=0.1)
