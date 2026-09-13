"""
Descrição: Verifica o consumo MQTT do estado operacional do Edge.
Autor: Leôncio Ferreira
"""

import asyncio

from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.operations.dto import StationCreateDTO
from app.modules.operations.messaging.device_status_handler import (
    DeviceStatusMessageHandler,
)
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


async def receive_status_message() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    service = OperationsService(OperationsRepository())
    async with SessionFactory() as session:
        station = await service.create_station(
            session,
            StationCreateDTO(
                code="envase-01",
                name="Estação de envase 01",
                device_id="leocio-raspberry",
            ),
        )

    await DeviceStatusMessageHandler()(
        b'''{
            "device_id": "leocio-raspberry",
            "connection": "ONLINE",
            "camera": "ONLINE",
            "processing": "ONLINE",
            "timestamp": "2026-09-13T10:00:00-03:00"
        }'''
    )

    async with SessionFactory() as session:
        status = await service.find_station_status(session, station.id)

    assert status is not None
    assert status.connection == "ONLINE"


def test_handler_persists_device_status_from_mqtt() -> None:
    asyncio.run(receive_status_message())
