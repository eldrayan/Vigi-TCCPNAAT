"""
Descrição: Verifica os comandos de inicialização e limpeza do ambiente local.
Autor: Leôncio Ferreira
"""

from pathlib import Path


def makefile() -> str:
    return (Path(__file__).parents[1] / "Makefile").read_text(encoding="utf-8")


def test_up_reloads_environment_before_starting_compose() -> None:
    content = makefile()

    assert "up: ensure-env\n\t$(MAKE) --no-print-directory compose-up" in content
    assert "compose-up:\n\tdocker compose up --build --detach" in content


def test_reset_data_removes_backend_volume_and_starts_clean_stack() -> None:
    content = makefile()

    assert "reset-data:\n\tdocker compose down" in content
    assert "docker volume rm vigi_backend_data" in content
    assert "$(MAKE) --no-print-directory up" in content
