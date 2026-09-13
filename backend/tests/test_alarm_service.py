"""
Descrição: Verifica a geração de alarme ao ultrapassar o limite do lote.
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


async def evaluate_alarm() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    operations = OperationsService(OperationsRepository())
    inspections = InspectionRepository()
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
            SetNonconformityLimitDTO(max_nonconformity_rate=5),
        )
        inspection = await inspections.create(
            session,
            InspectionCreateDTO(
                inspection_id=1,
                timestamp=datetime.now(UTC),
                station_code="envase-01",
                batch_code="LOTE-001",
                result="NAO_CONFORME",
                category="ANOMALIA_PRODUTO",
                nonconformity_type="SEM_TAMPA",
                confidence=0.99,
                processing_time_ms=100,
                model_format="pytorch",
            ),
        )
        alarm = await AlarmService().evaluate(session, inspection.inspection_id)

    assert alarm is not None
    assert alarm.alarm_type == "LIMITE_NAO_CONFORMIDADE"
    assert alarm.rate == 100
    assert alarm.threshold == 5


def test_creates_alarm_when_batch_rate_exceeds_limit() -> None:
    asyncio.run(evaluate_alarm())
