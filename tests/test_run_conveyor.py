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
