"""Contrato do evento de inspeção publicado pelo Edge."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from edge.inference.schemas import InspectionDecision


@dataclass(frozen=True)
class InspectionEvent:
    inspection_id: int
    timestamp: str
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
        timestamp: datetime | None = None,
        inspection_id: int | None = None,
    ) -> InspectionEvent:
        occurred_at = timestamp or datetime.now(UTC)
        event_id = inspection_id or time.time_ns() // 1_000
        return cls(
            inspection_id=event_id,
            timestamp=occurred_at.isoformat(),
            **decision.as_dict(),
        )

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
