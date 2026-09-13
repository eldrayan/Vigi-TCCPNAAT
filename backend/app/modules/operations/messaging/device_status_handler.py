"""
Descrição: Valida e persiste estados operacionais recebidos do Edge pelo MQTT.
Autor: Leôncio Ferreira
"""

import logging

from pydantic import ValidationError

from app.infrastructure.database import SessionFactory
from app.modules.operations.dto import DeviceStatusDTO, DeviceStatusMessageDTO
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService

logger = logging.getLogger(__name__)


class DeviceStatusMessageHandler:
    """Consome a última telemetria de disponibilidade de cada dispositivo."""

    def __init__(self) -> None:
        self.service = OperationsService(OperationsRepository())

    async def __call__(self, payload: bytes) -> None:
        try:
            message = DeviceStatusMessageDTO.model_validate_json(payload)
        except ValidationError:
            logger.exception("Payload de estado do dispositivo inválido.")
            return

        status = DeviceStatusDTO(
            connection=message.connection,
            camera=message.camera,
            processing=message.processing,
            timestamp=message.timestamp,
        )
        async with SessionFactory() as session:
            await self.service.report_device_status(session, message.device_id, status)

        logger.info("Estado do dispositivo %s persistido.", message.device_id)
