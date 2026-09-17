"""
Descrição: Testa a compatibilidade do ponto de entrada da esteira.
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


def test_entrypoint_exposes_the_station_parser() -> None:
    args = load_module().build_parser().parse_args(
        ["--station-code", "ESTACAO_02", "--batch-code", "LOTE_02"]
    )

    assert (args.station_code, args.batch_code) == ("ESTACAO_02", "LOTE_02")


def test_inspection_publisher_uses_device_specific_client_id() -> None:
    content = (
        Path(__file__).parents[1] / "scripts" / "run_conveyor.py"
    ).read_text(encoding="utf-8")

    assert 'client_id=f"vigi-edge-{args.device_id}"' in content


def test_readiness_diagnostic_uses_requested_station_code() -> None:
    content = (
        Path(__file__).parents[1] / "scripts" / "run_conveyor.py"
    ).read_text(encoding="utf-8")

    assert 'print(f"\\nDiagnóstico de prontidão — {args.station_code}")' in content
