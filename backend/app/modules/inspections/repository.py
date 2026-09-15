"""
Descrição: Implementa a persistência e as consultas de inspeções no SQLite.
Autor: Leôncio Ferreira
"""

from sqlalchemy import case, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.operations.model import Batch, Station

from .dto import InspectionCreateDTO, InspectionFilterDTO
from .model import Inspection


class InspectionRepository:
    async def create(
        self,
        session: AsyncSession,
        dto: InspectionCreateDTO,
    ) -> Inspection:
        station_id = None
        batch_id = None

        async with session.begin():
            if dto.station_code is not None and dto.batch_code is not None:
                context = await session.execute(
                    select(Station.id, Batch.id)
                    .join(Batch, Batch.station_id == Station.id)
                    .where(
                        func.lower(func.replace(Station.code, "_", "-"))
                        == func.lower(func.replace(dto.station_code, "_", "-")),
                        func.lower(func.replace(Batch.code, "_", "-"))
                        == func.lower(func.replace(dto.batch_code, "_", "-")),
                    )
                )
                row = context.one_or_none()
                if row is None:
                    raise LookupError("Estação ou lote não cadastrado.")
                station_id, batch_id = row

            values = {
                "inspection_id": dto.inspection_id,
                "timestamp": dto.timestamp,
                "station_code": dto.station_code,
                "batch_code": dto.batch_code,
                "station_id": station_id,
                "batch_id": batch_id,
                "result": dto.result.value,
                "category": (dto.category.value if dto.category is not None else None),
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
                "model_format": dto.model_format,
            }
            statement = (
                insert(Inspection)
                .values(**values)
                .on_conflict_do_nothing(index_elements=[Inspection.inspection_id])
            )
            await session.execute(statement)
            result = await session.execute(
                select(Inspection).where(Inspection.inspection_id == dto.inspection_id)
            )
            inspection = result.scalar_one()

        return inspection

    async def find_all(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        filters: InspectionFilterDTO | None = None,
    ) -> list[Inspection]:
        statement = self.apply_filters(select(Inspection), filters)
        result = await session.execute(
            statement.order_by(Inspection.timestamp.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count(
        self,
        session: AsyncSession,
        filters: InspectionFilterDTO | None = None,
    ) -> int:
        statement = self.apply_filters(
            select(func.count(Inspection.inspection_id)), filters
        )
        result = await session.execute(statement)
        return result.scalar_one()

    async def find_by_id(
        self,
        session: AsyncSession,
        inspection_id: int,
    ) -> Inspection | None:
        return await session.get(Inspection, inspection_id)

    async def get_summary(
        self,
        session: AsyncSession,
        filters: InspectionFilterDTO | None = None,
    ) -> dict[str, int | float]:
        statement = select(
            func.count(Inspection.inspection_id),
            func.sum(case((Inspection.result == "CONFORME", 1), else_=0)),
            func.sum(case((Inspection.result == "NAO_CONFORME", 1), else_=0)),
            func.sum(
                case((Inspection.nonconformity_type == "SEM_TAMPA", 1), else_=0)
            ),
            func.sum(
                case((Inspection.nonconformity_type == "TAMPA_TORTA", 1), else_=0)
            ),
            func.sum(
                case((Inspection.nonconformity_type == "AMASSADO", 1), else_=0)
            ),
            func.sum(case((Inspection.category == "FALHA_TECNICA", 1), else_=0)),
        )
        result = await session.execute(self.apply_filters(statement, filters))
        (
            total,
            compliant,
            noncompliant,
            sem_tampa,
            tampa_torta,
            amassado,
            falha_tecnica,
        ) = result.one()
        tot = total or 0
        comp = compliant or 0
        noncomp = noncompliant or 0
        rate = round((comp / tot * 100), 2) if tot > 0 else 100.0
        return {
            "total": tot,
            "compliant": comp,
            "noncompliant": noncomp,
            "compliance_rate": rate,
            "sem_tampa": sem_tampa or 0,
            "tampa_torta": tampa_torta or 0,
            "amassado": amassado or 0,
            "falha_tecnica": falha_tecnica or 0,
        }

    @staticmethod
    def apply_filters(statement, filters: InspectionFilterDTO | None):
        if filters is None:
            return statement
        if filters.station_code is not None:
            statement = statement.where(
                func.lower(func.replace(Inspection.station_code, "_", "-"))
                == func.lower(func.replace(filters.station_code, "_", "-"))
            )
        if filters.batch_code is not None:
            statement = statement.where(
                func.lower(func.replace(Inspection.batch_code, "_", "-"))
                == func.lower(func.replace(filters.batch_code, "_", "-"))
            )
        if filters.result is not None:
            statement = statement.where(Inspection.result == filters.result.value)
        if filters.nonconformity_type is not None:
            statement = statement.where(
                Inspection.nonconformity_type == filters.nonconformity_type.value
            )
        if filters.start_at is not None:
            statement = statement.where(Inspection.timestamp >= filters.start_at)
        if filters.end_at is not None:
            statement = statement.where(Inspection.timestamp <= filters.end_at)
        return statement
