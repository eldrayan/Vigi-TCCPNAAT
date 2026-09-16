"""
Descrição: Calcula taxas de não conformidade e gera alarmes por lote.
Autor: Leôncio Ferreira
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inspections.model import Inspection
from app.modules.operations.model import Batch

from .dto import AlarmResponseDTO
from .repository import AlarmRepository


class AlarmService:
    def __init__(self, repository: AlarmRepository | None = None) -> None:
        self.repository = repository or AlarmRepository()

    async def evaluate(
        self, session: AsyncSession, inspection_id: int
    ) -> AlarmResponseDTO | None:
        inspection = await session.get(Inspection, inspection_id)
        if inspection is None or inspection.result != "NAO_CONFORME":
            return None
        if inspection.batch_id is None or inspection.station_id is None:
            return None

        batch = await session.get(Batch, inspection.batch_id)
        if batch is None:
            return None

        now = datetime.now(UTC)

        # 1. RN05: Alarme de não-conformidades recorrentes / consecutivas
        consecutive_threshold = 3
        recent_results = (
            await session.scalars(
                select(Inspection.result)
                .where(Inspection.batch_id == batch.id)
                .order_by(Inspection.timestamp.desc(), Inspection.inspection_id.desc())
                .limit(consecutive_threshold)
            )
        ).all()

        if (
            len(recent_results) == consecutive_threshold
            and all(r == "NAO_CONFORME" for r in recent_results)
        ):
            open_consecutive = await self.repository.find_open(
                session, batch.id, alarm_type="FALHAS_RECORRENTES"
            )
            if open_consecutive is None:
                latest_consecutive = await self.repository.find_latest(
                    session, batch.id, alarm_type="FALHAS_RECORRENTES"
                )
                if latest_consecutive is None:
                    alarm = await self.repository.create_open(
                        session,
                        station_id=inspection.station_id,
                        batch_id=batch.id,
                        alarm_type="FALHAS_RECORRENTES",
                        rate=float(consecutive_threshold),
                        threshold=float(consecutive_threshold),
                        name="Falhas recorrentes consecutivas",
                        created_at=now,
                    )
                    return AlarmResponseDTO.model_validate(alarm)

        # 2. Alarme por Limite de Não Conformidade do Lote (US02)
        if batch.max_nonconformity_rate is not None:
            result = await session.execute(
                select(
                    func.count(Inspection.inspection_id),
                    func.sum(func.iif(Inspection.result == "NAO_CONFORME", 1, 0)),
                ).where(Inspection.batch_id == batch.id)
            )
            total, nonconforming = result.one()
            rate = (nonconforming or 0) * 100 / total if total else 0
            if rate > batch.max_nonconformity_rate:
                existing = await self.repository.find_open(
                    session, batch.id, alarm_type="LIMITE_NAO_CONFORMIDADE"
                )
                if existing is None:
                    latest = await self.repository.find_latest(
                        session, batch.id, alarm_type="LIMITE_NAO_CONFORMIDADE"
                    )
                    if latest is None:
                        alarm = await self.repository.create_open(
                            session,
                            station_id=inspection.station_id,
                            batch_id=batch.id,
                            alarm_type="LIMITE_NAO_CONFORMIDADE",
                            rate=rate,
                            threshold=batch.max_nonconformity_rate,
                            name=batch.alarm_name or "Alarme de qualidade",
                            created_at=now,
                        )
                        return AlarmResponseDTO.model_validate(alarm)

        return None

    async def list_all(self, session: AsyncSession) -> list[AlarmResponseDTO]:
        return [
            AlarmResponseDTO.model_validate(item)
            for item in await self.repository.list_all(session)
        ]

    async def acknowledge(
        self, session: AsyncSession, alarm_id: int, acknowledged_by: str
    ) -> AlarmResponseDTO | None:
        alarm = await self.repository.acknowledge(
            session, alarm_id, acknowledged_by
        )
        if alarm is None:
            return None
        return AlarmResponseDTO.model_validate(alarm)
