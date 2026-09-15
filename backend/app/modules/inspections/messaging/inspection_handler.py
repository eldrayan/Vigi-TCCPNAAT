"""
Descrição: Valida e persiste mensagens MQTT de inspeção recebidas do edge.
Autor: Leôncio Ferreira
"""

import logging

from pydantic import ValidationError

from app.infrastructure.database import SessionFactory
from app.infrastructure.events import EventBus
from app.modules.alarms.service import AlarmService
from app.modules.inspections.dto import InspectionCreateDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.inspections.service import InspectionService

logger = logging.getLogger(__name__)


class InspectionMessageHandler:
    def __init__(
        self,
        event_bus: EventBus | None = None,
        producer=None,
        topic_alarms: str | None = None,
    ) -> None:
        self.service = InspectionService(InspectionRepository())
        self.alarm_service = AlarmService()
        self.event_bus = event_bus
        self.producer = producer
        self.topic_alarms = topic_alarms

    async def __call__(self, payload: bytes) -> None:
        try:
            dto = InspectionCreateDTO.model_validate_json(payload)
        except ValidationError:
            logger.exception("Payload de inspeção inválido.")
            return

        logger.info("Inspeção %s recebida via MQTT.", dto.inspection_id)

        async with SessionFactory() as session:
            await self.service.create(session, dto)
            alarm = await self.alarm_service.evaluate(session, dto.inspection_id)

        if alarm is not None:
            alarm_payload = alarm.model_dump(mode="json")
            if self.event_bus is not None:
                await self.event_bus.publish("alarm.created", alarm_payload)
            if self.producer is not None and self.topic_alarms:
                self.producer.publish(
                    topic=self.topic_alarms,
                    payload=alarm_payload,
                    qos=1,
                )

        if self.event_bus is not None:
            await self.event_bus.publish(
                "inspection.created", dto.model_dump(mode="json")
            )

        logger.info(
            "Inspeção %s persistida com sucesso.",
            dto.inspection_id,
        )
