"""Objetos de dados produzidos pelo motor de inferencia."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Classification:
    class_name: str
    confidence: float


@dataclass(frozen=True)
class InspectionDecision:
    result: str
    category: str | None
    nonconformity_type: str | None
    technical_failure_type: str | None
    confidence: float | None
    processing_time_ms: float
    model_format: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
