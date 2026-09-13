"""
Descrição: Coordena os casos de uso de estações, lotes e contexto operacional.
Autor: Leôncio Ferreira
"""

from sqlalchemy.ext.asyncio import AsyncSession

from .dto import (
    BatchCreateDTO,
    BatchResponseDTO,
    DeviceStatusDTO,
    OperationalContextDTO,
    SetNonconformityLimitDTO,
    StationCreateDTO,
    StationResponseDTO,
)
from .repository import OperationsRepository


class OperationsService:
    def __init__(self, repository: OperationsRepository) -> None:
        self.repository = repository

    async def create_station(
        self, session: AsyncSession, dto: StationCreateDTO
    ) -> StationResponseDTO:
        station = await self.repository.create_station(session, dto)
        return StationResponseDTO.model_validate(station)

    async def list_stations(self, session: AsyncSession) -> list[StationResponseDTO]:
        return [
            StationResponseDTO.model_validate(item)
            for item in await self.repository.list_stations(session)
        ]

    async def find_station(
        self, session: AsyncSession, station_id: int
    ) -> StationResponseDTO | None:
        station = await self.repository.find_station(session, station_id)
        if station is None:
            return None
        return StationResponseDTO.model_validate(station)

    async def report_device_status(
        self,
        session: AsyncSession,
        device_id: str,
        dto: DeviceStatusDTO,
    ) -> DeviceStatusDTO:
        status = await self.repository.update_device_status(session, device_id, dto)
        return DeviceStatusDTO(
            connection=status.connection,
            camera=status.camera,
            processing=status.processing,
            timestamp=status.reported_at,
        )

    async def find_station_status(
        self, session: AsyncSession, station_id: int
    ) -> DeviceStatusDTO | None:
        status = await self.repository.find_station_status(session, station_id)
        if status is None:
            return None
        return DeviceStatusDTO(
            connection=status.connection,
            camera=status.camera,
            processing=status.processing,
            timestamp=status.reported_at,
        )

    async def create_batch(
        self, session: AsyncSession, station_id: int, dto: BatchCreateDTO
    ) -> BatchResponseDTO:
        batch = await self.repository.create_batch(session, station_id, dto)
        return BatchResponseDTO.model_validate(batch)

    async def list_batches(
        self, session: AsyncSession, station_id: int
    ) -> list[BatchResponseDTO]:
        if await self.repository.find_station(session, station_id) is None:
            raise LookupError("Estação não encontrada.")
        return [
            BatchResponseDTO.model_validate(item)
            for item in await self.repository.list_batches(session, station_id)
        ]

    async def activate_batch(
        self, session: AsyncSession, station_id: int, batch_id: int
    ) -> tuple[OperationalContextDTO, str]:
        batch, station = await self.repository.activate_batch(
            session, station_id, batch_id
        )
        context = OperationalContextDTO(
            station_code=station.code, batch_code=batch.code
        )
        return context, station.device_id

    async def set_nonconformity_limit(
        self,
        session: AsyncSession,
        station_id: int,
        batch_id: int,
        dto: SetNonconformityLimitDTO,
    ) -> BatchResponseDTO:
        batch = await self.repository.set_nonconformity_limit(
            session, station_id, batch_id, dto
        )
        return BatchResponseDTO.model_validate(batch)
