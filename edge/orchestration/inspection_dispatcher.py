"""
Descrição: Entrega inspeções e alarmes produzidos pela esteira.
Autor: Leôncio Ferreira
"""

from __future__ import annotations

from edge.inference.schemas import InspectionDecision
from edge.messaging.context import OperationalContext
from edge.messaging.event import InspectionEvent
from edge.messaging.outbox import InspectionOutbox
from edge.messaging.publisher import MQTTInspectionPublisher
from edge.messaging.synchronizer import InspectionOutboxSynchronizer


class InspectionDispatcher:
    def __init__(
        self,
        publisher: MQTTInspectionPublisher,
        outbox: InspectionOutbox | None = None,
    ) -> None:
        self.publisher = publisher
        self.outbox = outbox
        self.synchronizer = (
            InspectionOutboxSynchronizer(outbox, publisher) if outbox else None
        )

    def dispatch(
        self,
        decision: InspectionDecision,
        context: OperationalContext | None,
    ) -> InspectionEvent:
        event = InspectionEvent.from_decision(decision, context=context)
        if self.outbox is None:
            self.publisher.publish_inspection(event)
        else:
            self.outbox.enqueue(event)
            if self.synchronizer is not None:
                self.synchronizer.synchronize_once()
        self._publish_alarm(decision, event)
        return event

    def _publish_alarm(
        self, decision: InspectionDecision, event: InspectionEvent
    ) -> None:
        if decision.result == "CONFORME" and decision.technical_failure_type is None:
            return
        alert_name = (
            decision.technical_failure_type
            or decision.nonconformity_type
            or "ALERTA"
        )
        self.publisher.publish_alarm(
            {
                "inspection_id": event.inspection_id,
                "timestamp": event.timestamp,
                "alert_type": alert_name,
                "severity": "CRITICAL"
                if decision.technical_failure_type
                else "WARNING",
                "message": f"Não conformidade detectada: {alert_name}",
            }
        )
