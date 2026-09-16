"""
Descrição: Verifica que o alarme consecutivo não dispara novamente no mesmo lote.
Autor: Leôncio Ferreira
"""

import asyncio
from datetime import datetime, timedelta

from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.alarms.service import AlarmService
from app.modules.inspections.dto import InspectionCreateDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.operations.dto import BatchCreateDTO, StationCreateDTO
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


def inspection(inspection_id: int, timestamp: datetime) -> InspectionCreateDTO:
    return InspectionCreateDTO(
        inspection_id=inspection_id,
        timestamp=timestamp,
        station_code="envase-01",
        batch_code="LOTE-001",
        result="NAO_CONFORME",
        category="ANOMALIA_PRODUTO",
        nonconformity_type="SEM_TAMPA",
        confidence=0.99,
        processing_time_ms=100,
        model_format="pytorch",
    )


async def evaluate_consecutive_after_acknowledgement() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    operations = OperationsService(OperationsRepository())
    inspections = InspectionRepository()
    service = AlarmService()
    async with SessionFactory() as session:
        station = await operations.create_station(
            session,
            StationCreateDTO(
                code="envase-01",
                name="Estação de envase 01",
                device_id="rasp-01",
            ),
        )
        await operations.create_batch(
            session, station.id, BatchCreateDTO(code="LOTE-001")
        )
        initial_time = datetime.now().astimezone() - timedelta(seconds=10)
        for inspection_id in range(1, 4):
            created = await inspections.create(
                session, inspection(inspection_id, initial_time)
            )
        alarm = await service.evaluate(session, created.inspection_id)
        assert alarm is not None
        await service.acknowledge(session, alarm.id, "operador")

        for inspection_id in range(4, 7):
            created = await inspections.create(
                session,
                inspection(
                    inspection_id,
                    alarm.created_at + timedelta(seconds=inspection_id),
                ),
            )
        repeated = await service.evaluate(session, created.inspection_id)

        assert repeated is None
        assert len(await service.list_all(session)) == 1


def test_acknowledged_consecutive_alarm_does_not_trigger_again() -> None:
    asyncio.run(evaluate_consecutive_after_acknowledgement())
