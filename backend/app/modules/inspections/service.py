"""
Descrição: Coordena as regras e os casos de uso relacionados às inspeções.
Autor: Leôncio Ferreira
"""

from sqlalchemy.ext.asyncio import AsyncSession

from .dto import (
    InspectionCreateDTO,
    InspectionResponseDTO,
    InspectionSummaryDTO,
)
from .repository import InspectionRepository


class InspectionService:
    def __init__(self, repository: InspectionRepository) -> None:
        self.repository = repository

    async def create(
        self,
        session: AsyncSession,
        dto: InspectionCreateDTO,
    ) -> InspectionResponseDTO:
        inspection = await self.repository.create(session, dto)

        return InspectionResponseDTO.model_validate(inspection)

    async def find_all(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
    ) -> list[InspectionResponseDTO]:
        inspections = await self.repository.find_all(session, limit, offset)
        return [
            InspectionResponseDTO.model_validate(inspection)
            for inspection in inspections
        ]

    async def find_by_id(
        self,
        session: AsyncSession,
        inspection_id: int,
    ) -> InspectionResponseDTO | None:
        inspection = await self.repository.find_by_id(session, inspection_id)
        if inspection is None:
            return None
        return InspectionResponseDTO.model_validate(inspection)

    async def get_summary(
        self,
        session: AsyncSession,
    ) -> InspectionSummaryDTO:
        total, compliant, noncompliant = await self.repository.get_summary(session)
        return InspectionSummaryDTO(
            total=total,
            compliant=compliant,
            noncompliant=noncompliant,
        )
