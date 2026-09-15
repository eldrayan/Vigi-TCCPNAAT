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
