"""Expõe as rotas de configuração de estações e lotes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session

from .dto import (
    BatchCreateDTO,
    BatchResponseDTO,
    OperationalContextDTO,
    SetActiveBatchDTO,
    StationCreateDTO,
    StationResponseDTO,
)
from .repository import OperationsRepository
from .service import OperationsService

router = APIRouter(prefix="/api/estacoes", tags=["operations"])
service = OperationsService(OperationsRepository())
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


@router.post("", response_model=StationResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_station(
    dto: StationCreateDTO, session: SessionDependency
) -> StationResponseDTO:
    try:
        return await service.create_station(session, dto)
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Código da estação ou dispositivo já cadastrado.",
        ) from error


@router.get("", response_model=list[StationResponseDTO])
async def list_stations(session: SessionDependency) -> list[StationResponseDTO]:
    return await service.list_stations(session)


@router.get("/{station_id}", response_model=StationResponseDTO)
async def get_station(
    station_id: int, session: SessionDependency
) -> StationResponseDTO:
    station = await service.find_station(session, station_id)
    if station is None:
        raise not_found("Estação não encontrada.")
    return station


@router.post(
    "/{station_id}/lotes",
    response_model=BatchResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_batch(
    station_id: int, dto: BatchCreateDTO, session: SessionDependency
) -> BatchResponseDTO:
    try:
        return await service.create_batch(session, station_id, dto)
    except LookupError as error:
        raise not_found(str(error)) from error
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lote já cadastrado nesta estação.",
        ) from error


@router.get("/{station_id}/lotes", response_model=list[BatchResponseDTO])
async def list_batches(
    station_id: int, session: SessionDependency
) -> list[BatchResponseDTO]:
    try:
        return await service.list_batches(session, station_id)
    except LookupError as error:
        raise not_found(str(error)) from error


@router.put("/{station_id}/lote-ativo", response_model=OperationalContextDTO)
async def set_active_batch(
    station_id: int,
    dto: SetActiveBatchDTO,
    session: SessionDependency,
    request: Request,
) -> OperationalContextDTO:
    try:
        context, device_id = await service.activate_batch(
            session, station_id, dto.batch_id
        )
    except LookupError as error:
        raise not_found(str(error)) from error

    payload = context.model_dump()
    request.app.state.mqtt_producer.publish(
        topic=f"vigi/dispositivos/{device_id}/configuracao",
        payload=payload,
        qos=1,
        retain=True,
    )
    return context
