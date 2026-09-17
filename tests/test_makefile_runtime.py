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


def test_preview_camera_exposes_framing_options() -> None:
    content = makefile()

    assert "preview-camera:\n\t$(UV_RUN) python scripts/preview_camera.py" in content
    assert '--camera-id "$(CAMERA)"' in content
    assert '--width "$(WIDTH)"' in content
    assert '--height "$(HEIGHT)"' in content
    assert '--port "$(PREVIEW_PORT)"' in content


def test_compose_control_commands_do_not_require_backend_credentials() -> None:
    content = makefile()

    assert "COMPOSE_CONTROL_ENV =" in content
    assert "down:\n\t$(COMPOSE_CONTROL_ENV) docker compose down" in content
    assert "ps:\n\t$(COMPOSE_CONTROL_ENV) docker compose ps" in content
    assert "logs:\n\t$(COMPOSE_CONTROL_ENV) docker compose logs --follow" in content
