"""Valida a execução isolada da sincronização da fila offline."""

from datetime import UTC, datetime

from edge.messaging.synchronizer import InspectionOutboxSynchronizer


def test_synchronizer_delivers_pending_events_and_applies_retention() -> None:
    class Outbox:
        def __init__(self) -> None:
            self.publisher = None
            self.purge_arguments = None

        def deliver(self, publisher) -> int:
            self.publisher = publisher
            return 2

        def purge_expired(self, **kwargs) -> int:
            self.purge_arguments = kwargs
            return 0

    outbox = Outbox()
    publisher = object()
    synchronizer = InspectionOutboxSynchronizer(outbox, publisher)

    delivered = synchronizer.synchronize_once(now=datetime(2026, 9, 13, tzinfo=UTC))

    assert delivered == 2
    assert outbox.publisher is publisher
    assert outbox.purge_arguments["now"] == datetime(2026, 9, 13, tzinfo=UTC)
