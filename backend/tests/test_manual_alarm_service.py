"""Valida a criação manual de alarmes exibidos pelo dashboard."""

import asyncio

import pytest
from app.infrastructure.database import Base, SessionFactory, engine
from app.modules.alarms.dto import AlarmCreateDTO
from app.modules.alarms.service import AlarmService
from app.modules.operations.dto import BatchCreateDTO, StationCreateDTO
from app.modules.operations.repository import OperationsRepository
from app.modules.operations.service import OperationsService


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def create_manual_alarm() -> None:
    await reset_database()
    operations = OperationsService(OperationsRepository())
    alarms = AlarmService()

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
        created = await alarms.create_manual(
            session,
            AlarmCreateDTO(
                station_id=station.id,
                batch_id=batch.id,
                name="Qualidade da linha",
                threshold=20,
            ),
        )
        listed = await alarms.list_all(session)

    assert created.name == "Qualidade da linha"
    assert created.rate == 0
    assert created.status == "ABERTO"
    assert [alarm.id for alarm in listed] == [created.id]


async def reject_batch_from_another_station() -> None:
    await reset_database()
    operations = OperationsService(OperationsRepository())

    async with SessionFactory() as session:
        station_one = await operations.create_station(
            session,
            StationCreateDTO(code="envase-01", name="Estação 01", device_id="rasp-01"),
        )
        station_two = await operations.create_station(
            session,
            StationCreateDTO(code="envase-02", name="Estação 02", device_id="rasp-02"),
        )
        batch = await operations.create_batch(
            session, station_one.id, BatchCreateDTO(code="LOTE-001")
        )

        with pytest.raises(
            LookupError, match="Lote não encontrado para a estação selecionada"
        ):
            await AlarmService().create_manual(
                session,
                AlarmCreateDTO(
                    station_id=station_two.id,
                    batch_id=batch.id,
                    name="Contexto inválido",
                    threshold=10,
                ),
            )


def test_manual_alarm_is_created_and_listed_with_current_rate() -> None:
    asyncio.run(create_manual_alarm())


def test_manual_alarm_rejects_batch_from_another_station() -> None:
    asyncio.run(reject_batch_from_another_station())
