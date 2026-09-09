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
            "id_inspecao": dto.id_inspecao,
            "timestamp": dto.timestamp,
            "resultado": dto.resultado.value,
            "categoria": dto.categoria.value if dto.categoria is not None else None,
            "tipo_nao_conformidade": (
                dto.tipo_nao_conformidade.value
                if dto.tipo_nao_conformidade is not None
                else None
            ),
            "tipo_falha_tecnica": (
                dto.tipo_falha_tecnica.value
                if dto.tipo_falha_tecnica is not None
                else None
            ),
            "confianca": dto.confianca,
            "tempo_processamento_ms": dto.tempo_processamento_ms,
        }

        statement = (
            insert(Inspection)
            .values(**values)
            .on_conflict_do_nothing(index_elements=[Inspection.id_inspecao])
        )

        async with session.begin():
            await session.execute(statement)

            result = await session.execute(
                select(Inspection).where(
                    Inspection.id_inspecao == dto.id_inspecao
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
        id_inspecao: int,
    ) -> Inspection | None:
        return await session.get(Inspection, id_inspecao)

    async def get_summary(
        self,
        session: AsyncSession,
    ) -> tuple[int, int, int]:
        result = await session.execute(
            select(
                func.count(Inspection.id_inspecao),
                func.sum(
                    case((Inspection.resultado == "CONFORME", 1), else_=0)
                ),
                func.sum(
                    case((Inspection.resultado == "NAO_CONFORME", 1), else_=0)
                ),
            )
        )
        total, conformes, nao_conformes = result.one()
        return total or 0, conformes or 0, nao_conformes or 0
