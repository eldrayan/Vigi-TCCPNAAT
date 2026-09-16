#!/usr/bin/env python3
"""Cria ou completa o .env local sem sobrescrever configurações existentes."""

from __future__ import annotations

import argparse
import re
import secrets
from pathlib import Path

ENV_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
GENERATED_SECRET_KEYS = {"MQTT_BACKEND_PASSWORD", "MQTT_EDGE_PASSWORD"}


def configured_keys(content: str) -> set[str]:
    return {
        match.group(1)
        for line in content.splitlines()
        if (match := ENV_PATTERN.match(line))
    }


def default_lines(example_content: str) -> list[tuple[str, str]]:
    defaults: list[tuple[str, str]] = []
    for line in example_content.splitlines():
        match = ENV_PATTERN.match(line)
        if match:
            key, value = match.groups()
            defaults.append(
                (key, secrets.token_hex(24) if key in GENERATED_SECRET_KEYS else value)
            )
    return defaults


def ensure_env(
    env_path: Path,
    example_path: Path,
    *,
    create_only: bool = False,
    overrides: dict[str, str] | None = None,
) -> list[str]:
    if env_path.exists() and create_only:
        raise FileExistsError(
            ".env já existe; preserve-o ou remova-o conscientemente antes de recriar."
        )

    current = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    existing_keys = configured_keys(current)
    configured_defaults = overrides or {}
    missing = [
        (key, configured_defaults.get(key, value))
        for key, value in default_lines(example_path.read_text(encoding="utf-8"))
        if key not in existing_keys
    ]

    if missing:
        separator = "" if not current or current.endswith("\n") else "\n"
        additions = "\n".join(f"{key}={value}" for key, value in missing) + "\n"
        env_path.write_text(current + separator + additions, encoding="utf-8")

    env_path.chmod(0o600)
    return [key for key, _ in missing]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create-only", action="store_true")
    parser.add_argument("--frontend-port", default="8081")
    args = parser.parse_args()

    try:
        added = ensure_env(
            Path(".env"),
            Path(".env.example"),
            create_only=args.create_only,
            overrides={"FRONTEND_PORT": args.frontend_port},
        )
    except FileExistsError as error:
        parser.error(str(error))

    if added:
        print(f".env atualizado com configuração padrão: {', '.join(added)}")
    else:
        print(".env já contém toda a configuração padrão.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
