"""
Descrição: Expõe consultas e reconhecimento dos alarmes de produção.
Autor: Leôncio Ferreira
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session

from .dto import AcknowledgeAlarmDTO, AlarmResponseDTO
from .service import AlarmService

router = APIRouter(prefix="/api/alarmes", tags=["alarms"])
service = AlarmService()
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[AlarmResponseDTO])
async def list_alarms(session: SessionDependency) -> list[AlarmResponseDTO]:
    return await service.list_all(session)


@router.post("/{alarm_id}/reconhecer", response_model=AlarmResponseDTO)
async def acknowledge_alarm(
    alarm_id: int,
    dto: AcknowledgeAlarmDTO,
    session: SessionDependency,
) -> AlarmResponseDTO:
    alarm = await service.acknowledge(session, alarm_id, dto.acknowledged_by)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alarme não encontrado.",
        )
    return alarm
