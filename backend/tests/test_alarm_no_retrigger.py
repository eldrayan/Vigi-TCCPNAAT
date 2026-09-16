"""
Descrição: Verifica que um alarme reconhecido não dispara novamente no mesmo lote.
Autor: Leôncio Ferreira
"""

import asyncio
from datetime import UTC, datetime

from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.alarms.service import AlarmService
from app.modules.inspections.dto import InspectionCreateDTO
from app.modules.inspections.repository import InspectionRepository
from app.modules.operations.dto import (
    BatchCreateDTO,
    SetNonconformityLimitDTO,
    StationCreateDTO,
)
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


def inspection(inspection_id: int, result: str) -> InspectionCreateDTO:
    return InspectionCreateDTO(
        inspection_id=inspection_id,
        timestamp=datetime.now(UTC),
        station_code="envase-01",
        batch_code="LOTE-001",
        result=result,
        category="ANOMALIA_PRODUTO" if result == "NAO_CONFORME" else None,
        nonconformity_type="SEM_TAMPA" if result == "NAO_CONFORME" else None,
        confidence=0.99,
        processing_time_ms=100,
        model_format="pytorch",
    )


async def evaluate_after_acknowledgement() -> None:
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
        batch = await operations.create_batch(
            session, station.id, BatchCreateDTO(code="LOTE-001")
        )
        await operations.set_nonconformity_limit(
            session,
            station.id,
            batch.id,
            SetNonconformityLimitDTO(max_nonconformity_rate=20),
        )
        await inspections.create(session, inspection(1, "CONFORME"))
        first_nonconformity = await inspections.create(
            session, inspection(2, "NAO_CONFORME")
        )
        alarm = await service.evaluate(session, first_nonconformity.inspection_id)
        assert alarm is not None
        await service.acknowledge(session, alarm.id, "operador")

        second_nonconformity = await inspections.create(
            session, inspection(3, "NAO_CONFORME")
        )
        repeated = await service.evaluate(session, second_nonconformity.inspection_id)

        assert repeated is None
        assert len(await service.list_all(session)) == 1


def test_acknowledged_alarm_does_not_trigger_again_for_the_same_batch() -> None:
    asyncio.run(evaluate_after_acknowledgement())
