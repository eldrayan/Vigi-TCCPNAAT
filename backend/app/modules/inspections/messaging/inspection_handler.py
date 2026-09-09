"""
Descrição: Valida e persiste mensagens MQTT de inspeção recebidas do edge.
Autor: Leôncio Ferreira
"""

import logging

from pydantic import ValidationError

from app.infrastructure.database import SessionFactory
from app.modules.inspections.dto import InspectionCreateDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.inspections.service import InspectionService

logger = logging.getLogger(__name__)


class InspectionMessageHandler:
    def __init__(self) -> None:
        self.service = InspectionService(InspectionRepository())

    async def __call__(self, payload: bytes) -> None:
        try:
            dto = InspectionCreateDTO.model_validate_json(payload)
        except ValidationError:
            logger.exception("Payload de inspeção inválido.")
            return

        async with SessionFactory() as session:
            await self.service.create(session, dto)
