"""
Descrição: Verifica o estado atual de uma estação recebido pelo MQTT.
Autor: Leôncio Ferreira
"""

import asyncio
from datetime import datetime

from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.operations.dto import DeviceStatusDTO, StationCreateDTO
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


async def report_station_status() -> None:
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
        received = await service.report_device_status(
            session,
            "leocio-raspberry",
            DeviceStatusDTO(
                connection="ONLINE",
                camera="ONLINE",
                processing="ONLINE",
                timestamp=datetime.fromisoformat("2026-09-13T10:00:00-03:00"),
            ),
        )
        current = await service.find_station_status(session, station.id)

    assert received.connection == "ONLINE"
    assert current is not None
    assert current.camera == "ONLINE"
    assert current.processing == "ONLINE"


def test_service_persists_current_device_status() -> None:
    asyncio.run(report_station_status())
