"""
Descrição: Implementa a persistência e as consultas de inspeções no SQLite.
Autor: Leôncio Ferreira
"""

from sqlalchemy import case, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .dto import InspectionCreateDTO
from .model import Inspection


class InspectionRepository:
    async def create(
        self,
        session: AsyncSession,
        dto: InspectionCreateDTO,
    ) -> Inspection:
        values = {
            "inspection_id": dto.inspection_id,
            "timestamp": dto.timestamp,
            "result": dto.result.value,
            "category": dto.category.value if dto.category is not None else None,
            "nonconformity_type": (
                dto.nonconformity_type.value
                if dto.nonconformity_type is not None
                else None
            ),
            "technical_failure_type": (
                dto.technical_failure_type.value
                if dto.technical_failure_type is not None
                else None
            ),
            "confidence": dto.confidence,
            "processing_time_ms": dto.processing_time_ms,
        }

        statement = (
            insert(Inspection)
            .values(**values)
            .on_conflict_do_nothing(index_elements=[Inspection.inspection_id])
        )

        async with session.begin():
            await session.execute(statement)

            result = await session.execute(
                select(Inspection).where(
                    Inspection.inspection_id == dto.inspection_id
                )
            )
            inspection = result.scalar_one()

        return inspection

    async def find_all(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
    ) -> list[Inspection]:
        result = await session.execute(
            select(Inspection)
            .order_by(Inspection.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def find_by_id(
        self,
        session: AsyncSession,
        inspection_id: int,
    ) -> Inspection | None:
        return await session.get(Inspection, inspection_id)

    async def get_summary(
        self,
        session: AsyncSession,
    ) -> tuple[int, int, int]:
        result = await session.execute(
            select(
                func.count(Inspection.inspection_id),
                func.sum(
                    case((Inspection.result == "CONFORME", 1), else_=0)
                ),
                func.sum(
                    case((Inspection.result == "NAO_CONFORME", 1), else_=0)
                ),
            )
        )
        total, compliant, noncompliant = result.one()
        return total or 0, compliant or 0, noncompliant or 0
