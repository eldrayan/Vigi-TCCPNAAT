"""
Descrição: Valida persistência e troca do contexto operacional.
Autor: Leôncio Ferreira
"""

import asyncio
from datetime import UTC, datetime

from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.inspections.dto import InspectionCreateDTO, InspectionFilterDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.inspections.service import InspectionService
from app.modules.operations.dto import (
    BatchCreateDTO,
    ComponentStatus,
    DeviceStatusDTO,
    StationCreateDTO,
)
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def exercise_context_change() -> None:
    await reset_database()
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
        assert not session.in_transaction(), station.model_dump()
        first = await service.create_batch(
            session, station.id, BatchCreateDTO(code="LOTE-001")
        )
        second = await service.create_batch(
            session, station.id, BatchCreateDTO(code="LOTE-002")
        )

        context, device_id = await service.activate_batch(
            session, station.id, second.id
        )
        batches = await service.list_batches(session, station.id)
    async with SessionFactory() as session:
        inspection = await InspectionService(InspectionRepository()).create(
            session,
            InspectionCreateDTO(
                inspection_id=9001,
                timestamp=datetime.now(UTC),
                station_code=context.station_code,
                batch_code=context.batch_code,
                result="CONFORME",
                confidence=0.99,
                processing_time_ms=100,
                model_format="pytorch",
            ),
        )
        filtered = await InspectionService(InspectionRepository()).find_all(
            session,
            limit=10,
            offset=0,
            filters=InspectionFilterDTO(
                station_code="envase-01", batch_code="LOTE-002"
            ),
        )

    assert first.status == "ATIVO"
    assert context.station_code == "envase-01"
    assert context.batch_code == "LOTE-002"
    assert device_id == "leocio-raspberry"
    assert [batch.status for batch in batches] == ["ENCERRADO", "ATIVO"]
    assert inspection.station_code == "envase-01"
    assert inspection.batch_code == "LOTE-002"
    assert [item.inspection_id for item in filtered.items] == [9001]


def test_only_one_batch_remains_active_per_station() -> None:
    asyncio.run(exercise_context_change())


async def exercise_device_status() -> None:
    await reset_database()
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
        await service.report_device_status(
            session,
            station.device_id,
            DeviceStatusDTO(
                connection=ComponentStatus.ONLINE,
                sensor=ComponentStatus.ONLINE,
                camera=ComponentStatus.ONLINE,
                processing=ComponentStatus.IDLE,
                timestamp=datetime.now(UTC),
            ),
        )
        status = await service.find_station_status(session, station.id)

    assert status is not None
    assert status.sensor == ComponentStatus.ONLINE


def test_device_status_preserves_sensor_state() -> None:
    asyncio.run(exercise_device_status())
