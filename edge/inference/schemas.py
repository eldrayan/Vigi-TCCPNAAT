"""Objetos de dados produzidos pelo motor de inferencia."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Classification:
    class_name: str
    confidence: float


@dataclass(frozen=True)
class InspectionDecision:
    resultado: str
    categoria: str | None
    codigo: str | None
    confianca: float | None
    tempo_processamento_ms: float
    formato_modelo: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
