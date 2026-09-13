"""Normaliza identificadores operacionais usados em URLs e tópicos MQTT."""

import re
import unicodedata


def normalize_code(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    code = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    if not code:
        raise ValueError("O código deve possuir letras ou números.")
    return code
