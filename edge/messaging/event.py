"""Contrato do evento de inspeção publicado pelo Edge."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from edge.inference.schemas import InspectionDecision

from .context import OperationalContext


@dataclass(frozen=True)
class InspectionEvent:
    inspection_id: int
    timestamp: str
    station_code: str | None
    batch_code: str | None
    result: str
    category: str | None
    nonconformity_type: str | None
    technical_failure_type: str | None
    confidence: float | None
    processing_time_ms: float
    model_format: str

    @classmethod
    def from_decision(
        cls,
        decision: InspectionDecision,
        *,
        context: OperationalContext | None = None,
        timestamp: datetime | None = None,
        inspection_id: int | None = None,
    ) -> InspectionEvent:
        occurred_at = timestamp or datetime.now(UTC)
        event_id = inspection_id or time.time_ns() // 1_000
        return cls(
            inspection_id=event_id,
            timestamp=occurred_at.isoformat(),
            station_code=context.station_code if context else None,
            batch_code=context.batch_code if context else None,
            **decision.as_dict(),
        )

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> InspectionEvent:
        return cls(**payload)

    @property
    def inspections_topic(self) -> str:
        if self.station_code is None:
            raise ValueError("Evento sem estação não pode ser publicado na fila.")
        return f"vigi/estacoes/{self.station_code}/inspecoes"
