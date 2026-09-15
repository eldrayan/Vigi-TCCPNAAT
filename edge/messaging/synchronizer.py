"""Sincroniza em segundo plano as inspeções persistidas na fila do Edge."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol


class Outbox(Protocol):
    def deliver(self, publisher) -> int: ...

    def purge_expired(self, *, now: datetime, retention: timedelta) -> int: ...


class InspectionOutboxSynchronizer:
    def __init__(self, outbox: Outbox, publisher) -> None:
        self.outbox = outbox
        self.publisher = publisher

    def synchronize_once(self, *, now: datetime | None = None) -> int:
        current_time = now or datetime.now(UTC)
        delivered = self.outbox.deliver(self.publisher)
        self.outbox.purge_expired(
            now=current_time,
            retention=timedelta(days=30),
        )
        return delivered
