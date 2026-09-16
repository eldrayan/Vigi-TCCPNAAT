"""
Descrição: Testa a configuração de linha de comando da esteira.
Autor: Leôncio Ferreira
"""

from pathlib import Path

import pytest

from scripts.conveyor_cli import build_parser, validate_arguments


def test_parser_accepts_station_camera_and_capture_options(monkeypatch) -> None:
    monkeypatch.setenv("MQTT_EDGE_USERNAME", "edge-user")
    monkeypatch.setenv("MQTT_EDGE_PASSWORD", "edge-password")

    args = build_parser().parse_args(
        [
            "--station-code",
            "ESTACAO_02",
            "--device-id",
            "EDGE_02",
            "--batch-code",
            "LOTE_02",
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
            "--save-captures",
            "--capture-dir",
            "/tmp/vigi-captures",
        ]
    )

    assert (args.station_code, args.device_id, args.batch_code) == (
        "ESTACAO_02",
        "EDGE_02",
        "LOTE_02",
    )
    assert (args.width, args.height, args.fps) == (1296, 972, 40)
    assert (args.exposure_us, args.analogue_gain, args.capture_delay_ms) == (
        1000,
        4.0,
        180,
    )
    assert args.capture_dir == Path("/tmp/vigi-captures")
    assert (args.mqtt_username, args.mqtt_password) == (
        "edge-user",
        "edge-password",
    )


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--width", "0"], "width, height e fps devem ser positivos"),
        (["--exposure-us", "0"], "exposure-us deve ser positivo"),
        (["--analogue-gain", "0"], "analogue-gain deve ser positivo"),
        (["--capture-delay-ms", "-1"], "capture-delay-ms não pode ser negativo"),
    ],
)
def test_validate_arguments_rejects_invalid_camera_values(
    arguments: list[str], message: str
) -> None:
    args = build_parser().parse_args(arguments)

    with pytest.raises(SystemExit, match=message):
        validate_arguments(args)
