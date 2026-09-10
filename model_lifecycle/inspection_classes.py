"""Classes de inspecao reconhecidas pelo modelo do Vigi."""

from __future__ import annotations

CLASS_NAMES = (
    "01_conforme",
    "02_sem_tampa",
    "03_tampa_torta",
    "04_amassado",
)

CLASS_CODES = {
    "01_conforme": "CONFORME",
    "02_sem_tampa": "SEM_TAMPA",
    "03_tampa_torta": "TAMPA_TORTA",
    "04_amassado": "AMASSADO",
}


def canonical_class(value: str) -> str:
    """Aceita nomes com ou sem prefixo numerico e devolve o nome oficial."""
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {name: name for name in CLASS_NAMES}
    aliases.update({name.split("_", 1)[1]: name for name in CLASS_NAMES})
    try:
        return aliases[normalized]
    except KeyError as exc:
        raise ValueError(f"Classe desconhecida: {value}") from exc
