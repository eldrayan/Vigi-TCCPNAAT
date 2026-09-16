"""Testes da criação e reconciliação segura do arquivo .env."""

from pathlib import Path

import pytest

from scripts.configurar_env import ensure_env

EXAMPLE = """APP_ENV=development
FRONTEND_PORT=8081
MQTT_BACKEND_PASSWORD=troque-esta-senha
MQTT_EDGE_PASSWORD=troque-esta-senha
STATION_CODE=ESTACAO_01
"""


def test_creates_env_with_defaults_and_generated_secrets(tmp_path: Path) -> None:
    example = tmp_path / ".env.example"
    env = tmp_path / ".env"
    example.write_text(EXAMPLE, encoding="utf-8")

    added = ensure_env(env, example)
    content = env.read_text(encoding="utf-8")

    assert added == [
        "APP_ENV",
        "FRONTEND_PORT",
        "MQTT_BACKEND_PASSWORD",
        "MQTT_EDGE_PASSWORD",
        "STATION_CODE",
    ]
    assert "APP_ENV=development" in content
    assert "FRONTEND_PORT=8081" in content
    assert "troque-esta-senha" not in content
    assert env.stat().st_mode & 0o777 == 0o600


def test_adds_only_missing_defaults_to_existing_env(tmp_path: Path) -> None:
    example = tmp_path / ".env.example"
    env = tmp_path / ".env"
    example.write_text(EXAMPLE, encoding="utf-8")
    env.write_text(
        "APP_ENV=production\nMQTT_EDGE_PASSWORD=preservada\n",
        encoding="utf-8",
    )

    added = ensure_env(env, example)
    content = env.read_text(encoding="utf-8")

    assert added == ["FRONTEND_PORT", "MQTT_BACKEND_PASSWORD", "STATION_CODE"]
    assert "APP_ENV=production" in content
    assert "MQTT_EDGE_PASSWORD=preservada" in content
    assert content.count("APP_ENV=") == 1


def test_create_only_refuses_existing_env(tmp_path: Path) -> None:
    example = tmp_path / ".env.example"
    env = tmp_path / ".env"
    example.write_text(EXAMPLE, encoding="utf-8")
    env.write_text("APP_ENV=production\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        ensure_env(env, example, create_only=True)


def test_allows_overriding_a_missing_default(tmp_path: Path) -> None:
    example = tmp_path / ".env.example"
    env = tmp_path / ".env"
    example.write_text(EXAMPLE, encoding="utf-8")

    ensure_env(env, example, overrides={"FRONTEND_PORT": "9090"})

    assert "FRONTEND_PORT=9090" in env.read_text(encoding="utf-8")
