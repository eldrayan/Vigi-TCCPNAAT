"""Valida a fila persistente de inspeções pendentes do Edge."""

from datetime import UTC, datetime, timedelta

from edge.inference.schemas import InspectionDecision
from edge.messaging import InspectionEvent, InspectionOutbox, OperationalContext


def inspection(inspection_id: int) -> InspectionEvent:
    return InspectionEvent.from_decision(
        InspectionDecision(
            result="CONFORME",
            category=None,
            nonconformity_type=None,
            technical_failure_type=None,
            confidence=0.99,
            processing_time_ms=120,
            model_format="pytorch",
        ),
        context=OperationalContext("envase-01", "LOTE-001"),
        inspection_id=inspection_id,
        timestamp=datetime(2026, 9, 13, tzinfo=UTC),
    )


def test_outbox_persists_in_order_and_removes_only_after_delivery(tmp_path) -> None:
    outbox = InspectionOutbox(tmp_path / "outbox.db")
    outbox.enqueue(inspection(10))
    outbox.enqueue(inspection(11))

    assert [item.event.inspection_id for item in outbox.pending()] == [10, 11]

    class Publisher:
        def __init__(self) -> None:
            self.delivered: list[int] = []

        def publish(self, event: InspectionEvent, topic: str) -> None:
            self.delivered.append(event.inspection_id)
            if event.inspection_id == 11:
                raise ConnectionError("broker indisponível")

    publisher = Publisher()
    synchronized = outbox.deliver(publisher)

    assert synchronized == 1
    assert publisher.delivered == [10, 11]
    assert outbox.synchronization_status(10) == "SINCRONIZADO"
    assert outbox.synchronization_status(11) == "PENDENTE"
    assert [item.event.inspection_id for item in outbox.pending()] == [11]


def test_outbox_keeps_synchronized_events_for_thirty_days(tmp_path) -> None:
    outbox = InspectionOutbox(tmp_path / "outbox.db")
    outbox.enqueue(inspection(10))

    class Publisher:
        def publish(self, event: InspectionEvent, topic: str) -> None:
            return None

    outbox.deliver(Publisher(), synchronized_at=datetime(2026, 9, 13, tzinfo=UTC))
    removed = outbox.purge_expired(
        now=datetime(2026, 10, 14, tzinfo=UTC), retention=timedelta(days=30)
    )

    assert removed == 1


def test_outbox_recovers_last_operational_context_after_restart(tmp_path) -> None:
    path = tmp_path / "outbox.db"
    outbox = InspectionOutbox(path)
    context = OperationalContext("envase-01", "LOTE-001")

    outbox.save_context(context)

    assert InspectionOutbox(path).load_context() == context
