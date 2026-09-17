"""
Descrição: Expõe consultas e reconhecimento dos alarmes de produção.
Autor: Leôncio Ferreira
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session
from app.infrastructure.events import EventBus

from .dto import AcknowledgeAlarmDTO, AlarmCreateDTO, AlarmResponseDTO
from .service import AlarmService

router = APIRouter(prefix="/api/alarmes", tags=["alarms"])
service = AlarmService()
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[AlarmResponseDTO])
async def list_alarms(session: SessionDependency) -> list[AlarmResponseDTO]:
    return await service.list_all(session)


@router.post("", response_model=AlarmResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_alarm(
    dto: AlarmCreateDTO,
    session: SessionDependency,
    request: Request,
) -> AlarmResponseDTO:
    """
    Descrição: Cria um alarme manualmente a pedido do operador.
    Autor: Leôncio Ferreira
    """
    try:
        alarm = await service.create_manual(session, dto)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    event_bus: EventBus | None = getattr(request.app.state, "event_bus", None)
    if event_bus is not None:
        await event_bus.publish("alarm.created", alarm.model_dump(mode="json"))
    return alarm


@router.post("/{alarm_id}/reconhecer", response_model=AlarmResponseDTO)
async def acknowledge_alarm(
    alarm_id: int,
    dto: AcknowledgeAlarmDTO,
    session: SessionDependency,
    request: Request,
) -> AlarmResponseDTO:
    alarm = await service.acknowledge(session, alarm_id, dto.acknowledged_by)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alarme não encontrado.",
        )
    event_bus: EventBus | None = getattr(request.app.state, "event_bus", None)
    if event_bus is not None:
        await event_bus.publish("alarm.acknowledged", alarm.model_dump(mode="json"))
    return alarm
