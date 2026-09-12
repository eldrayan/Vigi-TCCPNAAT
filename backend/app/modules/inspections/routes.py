"""
Descrição: Expõe os endpoints HTTP de consulta do módulo de inspeções.
Autor: Leôncio Ferreira
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_session

from .dto import InspectionResponseDTO, InspectionSummaryDTO
from .repository import InspectionRepository
from .service import InspectionService

router = APIRouter(prefix="/api/inspecoes", tags=["inspections"])
service = InspectionService(InspectionRepository())

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[InspectionResponseDTO])
async def list_inspections(
    session: SessionDependency,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[InspectionResponseDTO]:
    return await service.find_all(session, limit, offset)


@router.get("/resumo", response_model=InspectionSummaryDTO)
async def get_summary(
    session: SessionDependency,
) -> InspectionSummaryDTO:
    return await service.get_summary(session)


@router.get("/{id_inspecao}", response_model=InspectionResponseDTO)
async def get_inspection(
    id_inspecao: int,
    session: SessionDependency,
) -> InspectionResponseDTO:
    inspection = await service.find_by_id(session, id_inspecao)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspeção não encontrada.")
    return inspection
