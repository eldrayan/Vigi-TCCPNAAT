"""
Descrição: Verifica a configuração de estação e dispositivo na CLI da esteira.
Autor: Leôncio Ferreira
"""

import importlib.util
from pathlib import Path


def load_module():
    script = Path(__file__).parents[1] / "scripts" / "run_conveyor.py"
    spec = importlib.util.spec_from_file_location("run_conveyor", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_accepts_station_and_device_identifiers() -> None:
    args = load_module().build_parser().parse_args(
        [
            "--station-code",
            "ESTACAO_02",
            "--device-id",
            "EDGE_02",
            "--batch-code",
            "LOTE_02",
        ]
    )

    assert args.station_code == "ESTACAO_02"
    assert args.device_id == "EDGE_02"
    assert args.batch_code == "LOTE_02"


def test_capture_saving_is_disabled_by_default() -> None:
    args = load_module().build_parser().parse_args([])

    assert args.save_captures is False
    assert args.capture_dir == Path("captures")


def test_accepts_capture_saving_and_custom_directory() -> None:
    args = load_module().build_parser().parse_args(
        ["--save-captures", "--capture-dir", "/tmp/vigi-captures"]
    )

    assert args.save_captures is True
    assert args.capture_dir == Path("/tmp/vigi-captures")


def test_accepts_camera_timing_controls() -> None:
    args = load_module().build_parser().parse_args(
        [
            "--width",
            "1296",
            "--height",
            "972",
            "--fps",
            "40",
            "--exposure-us",
            "1000",
            "--analogue-gain",
            "4.0",
            "--capture-delay-ms",
            "180",
        ]
    )

    assert (args.width, args.height, args.fps) == (1296, 972, 40)
    assert args.exposure_us == 1000
    assert args.analogue_gain == 4.0
    assert args.capture_delay_ms == 180


def test_reads_edge_mqtt_credentials_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("MQTT_EDGE_USERNAME", "edge-user")
    monkeypatch.setenv("MQTT_EDGE_PASSWORD", "edge-password")

    args = load_module().build_parser().parse_args([])

    assert args.mqtt_username == "edge-user"
    assert args.mqtt_password == "edge-password"
