"""
Descrição: Valida e persiste mensagens MQTT de inspeção recebidas do edge.
Autor: Leôncio Ferreira
"""

import logging

from pydantic import ValidationError

from app.infrastructure.database import SessionFactory
from app.infrastructure.events import EventBus
from app.modules.inspections.dto import InspectionCreateDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.inspections.service import InspectionService

logger = logging.getLogger(__name__)


class InspectionMessageHandler:
    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.service = InspectionService(InspectionRepository())
        self.event_bus = event_bus

    async def __call__(self, payload: bytes) -> None:
        try:
            dto = InspectionCreateDTO.model_validate_json(payload)
        except ValidationError:
            logger.exception("Payload de inspeção inválido.")
            return

        logger.info("Inspeção %s recebida via MQTT.", dto.inspection_id)

        async with SessionFactory() as session:
            await self.service.create(session, dto)

        if self.event_bus is not None:
            await self.event_bus.publish(
                "inspection.created", dto.model_dump(mode="json")
            )

        logger.info(
            "Inspeção %s persistida com sucesso.",
            dto.inspection_id,
        )
