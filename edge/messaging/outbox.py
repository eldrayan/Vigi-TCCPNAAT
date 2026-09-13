"""Mantém no Edge uma fila SQLite para entrega confiável das inspeções."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

from .context import OperationalContext
from .event import InspectionEvent


class InspectionPublisher(Protocol):
    def publish(self, event: InspectionEvent, topic: str) -> None: ...


@dataclass(frozen=True)
class PendingInspection:
    sequence: int
    topic: str
    event: InspectionEvent


class InspectionOutbox:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS inspection_outbox (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    inspection_id INTEGER NOT NULL UNIQUE,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    synchronized_at TEXT,
                    sync_status TEXT NOT NULL DEFAULT 'PENDENTE'
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS operational_context (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    station_code TEXT NOT NULL,
                    batch_code TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_inspection_outbox_pending
                ON inspection_outbox (sync_status, sequence)
                """
            )

    def enqueue(self, event: InspectionEvent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO inspection_outbox
                (inspection_id, topic, payload, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    event.inspection_id,
                    event.inspections_topic,
                    json.dumps(event.as_dict(), ensure_ascii=False),
                    event.timestamp,
                ),
            )

    def save_context(self, context: OperationalContext) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO operational_context
                (id, station_code, batch_code, updated_at)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    station_code = excluded.station_code,
                    batch_code = excluded.batch_code,
                    updated_at = excluded.updated_at
                """,
                (
                    context.station_code,
                    context.batch_code,
                    datetime.now(UTC).isoformat(),
                ),
            )

    def load_context(self) -> OperationalContext | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT station_code, batch_code
                FROM operational_context
                WHERE id = 1
                """
            ).fetchone()
        if row is None:
            return None
        return OperationalContext(station_code=row[0], batch_code=row[1])

    def pending(self) -> list[PendingInspection]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT sequence, topic, payload
                FROM inspection_outbox
                WHERE sync_status = 'PENDENTE'
                ORDER BY sequence
                """
            ).fetchall()
        return [
            PendingInspection(
                sequence=row[0],
                topic=row[1],
                event=InspectionEvent.from_dict(json.loads(row[2])),
            )
            for row in rows
        ]

    def deliver(
        self,
        publisher: InspectionPublisher,
        *,
        synchronized_at: datetime | None = None,
    ) -> int:
        delivered = 0
        for pending in self.pending():
            try:
                publisher.publish(pending.event, topic=pending.topic)
            except Exception:
                break
            self.mark_synchronized(
                pending.sequence,
                synchronized_at or datetime.now(UTC),
            )
            delivered += 1
        return delivered

    def mark_synchronized(self, sequence: int, synchronized_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE inspection_outbox
                SET synchronized_at = ?, sync_status = 'SINCRONIZADO'
                WHERE sequence = ?
                """,
                (synchronized_at.isoformat(), sequence),
            )

    def synchronization_status(self, inspection_id: int) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT sync_status
                FROM inspection_outbox
                WHERE inspection_id = ?
                """,
                (inspection_id,),
            ).fetchone()
        return row[0] if row is not None else None

    def purge_expired(self, *, now: datetime, retention: timedelta) -> int:
        cutoff = now - retention
        with self._connect() as connection:
            result = connection.execute(
                """
                DELETE FROM inspection_outbox
                WHERE synchronized_at IS NOT NULL AND synchronized_at < ?
                """,
                (cutoff.isoformat(),),
            )
        return result.rowcount

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        return connection
