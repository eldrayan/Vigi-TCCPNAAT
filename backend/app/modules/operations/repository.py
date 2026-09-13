"""
Descrição: Implementa a persistência de estações, lotes e contexto operacional.
Autor: Leôncio Ferreira
"""

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .dto import BatchCreateDTO, DeviceStatusDTO, StationCreateDTO
from .model import Batch, Station, StationStatus


class OperationsRepository:
    async def create_station(
        self, session: AsyncSession, dto: StationCreateDTO
    ) -> Station:
        station = Station(**dto.model_dump())
        async with session.begin():
            session.add(station)
            await session.flush()
        return station

    async def list_stations(self, session: AsyncSession) -> list[Station]:
        result = await session.execute(select(Station).order_by(Station.code))
        return list(result.scalars())

    async def find_station(
        self, session: AsyncSession, station_id: int
    ) -> Station | None:
        return await session.get(Station, station_id)

    async def update_device_status(
        self,
        session: AsyncSession,
        device_id: str,
        dto: DeviceStatusDTO,
    ) -> StationStatus:
        async with session.begin():
            station = await session.scalar(
                select(Station).where(Station.device_id == device_id)
            )
            if station is None:
                raise LookupError("Dispositivo sem estação cadastrada.")

            status = await session.get(StationStatus, station.id)
            if status is None:
                status = StationStatus(
                    station_id=station.id,
                    connection=dto.connection,
                    camera=dto.camera,
                    processing=dto.processing,
                    reported_at=dto.timestamp,
                )
                session.add(status)
            else:
                status.connection = dto.connection
                status.camera = dto.camera
                status.processing = dto.processing
                status.reported_at = dto.timestamp
            await session.flush()
        return status

    async def find_station_status(
        self, session: AsyncSession, station_id: int
    ) -> StationStatus | None:
        return await session.get(StationStatus, station_id)

    async def create_batch(
        self, session: AsyncSession, station_id: int, dto: BatchCreateDTO
    ) -> Batch:
        async with session.begin():
            if await session.get(Station, station_id) is None:
                raise LookupError("Estação não encontrada.")
            active = await session.scalar(
                select(Batch.id).where(
                    Batch.station_id == station_id,
                    Batch.status == "ATIVO",
                )
            )
            now = datetime.now(UTC)
            batch = Batch(
                station_id=station_id,
                code=dto.code,
                status="PENDENTE" if active is not None else "ATIVO",
                started_at=None if active is not None else now,
            )
            session.add(batch)
            await session.flush()
        return batch

    async def list_batches(self, session: AsyncSession, station_id: int) -> list[Batch]:
        result = await session.execute(
            select(Batch).where(Batch.station_id == station_id).order_by(Batch.id)
        )
        return list(result.scalars())

    async def find_batch(self, session: AsyncSession, batch_id: int) -> Batch | None:
        return await session.get(Batch, batch_id)

    async def activate_batch(
        self, session: AsyncSession, station_id: int, batch_id: int
    ) -> tuple[Batch, Station]:
        now = datetime.now(UTC)
        async with session.begin():
            station = await session.get(Station, station_id)
            if station is None:
                raise LookupError("Estação não encontrada.")
            await session.execute(
                update(Batch)
                .where(Batch.station_id == station_id, Batch.status == "ATIVO")
                .values(status="ENCERRADO", finished_at=now)
            )
            batch = await session.get(Batch, batch_id)
            if batch is None or batch.station_id != station_id:
                raise LookupError("Lote não encontrado para a estação.")
            batch.status = "ATIVO"
            batch.started_at = now
            batch.finished_at = None
        return batch, station
