"""
Descrição: Persiste e consulta alarmes gerados para os lotes.
Autor: Leôncio Ferreira
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import Alarm


class AlarmRepository:
    async def list_all(self, session: AsyncSession) -> list[Alarm]:
        result = await session.execute(select(Alarm).order_by(Alarm.created_at.desc()))
        return list(result.scalars())

    async def find_open(
        self, session: AsyncSession, batch_id: int, alarm_type: str | None = None
    ) -> Alarm | None:
        statement = select(Alarm).where(
            Alarm.batch_id == batch_id, Alarm.status == "ABERTO"
        )
        if alarm_type is not None:
            statement = statement.where(Alarm.alarm_type == alarm_type)
        return await session.scalar(statement)

    async def find_latest(
        self, session: AsyncSession, batch_id: int, alarm_type: str | None = None
    ) -> Alarm | None:
        statement = (
            select(Alarm)
            .where(Alarm.batch_id == batch_id)
            .order_by(Alarm.created_at.desc())
            .limit(1)
        )
        if alarm_type is not None:
            statement = statement.where(Alarm.alarm_type == alarm_type)
        return await session.scalar(statement)

    async def create_open(
        self,
        session: AsyncSession,
        *,
        station_id: int,
        batch_id: int,
        rate: float,
        threshold: float,
        alarm_type: str = "LIMITE_NAO_CONFORMIDADE",
        name: str = "Alarme de qualidade",
        created_at,
    ) -> Alarm:
        alarm = Alarm(
            station_id=station_id,
            batch_id=batch_id,
            alarm_type=alarm_type,
            name=name,
            rate=rate,
            threshold=threshold,
            status="ABERTO",
            created_at=created_at,
        )
        session.add(alarm)
        await session.flush()
        await session.commit()
        return alarm

    async def acknowledge(
        self, session: AsyncSession, alarm_id: int, acknowledged_by: str
    ) -> Alarm | None:
        async with session.begin():
            alarm = await session.get(Alarm, alarm_id)
            if alarm is None:
                return None
            alarm.status = "RECONHECIDO"
            alarm.acknowledged_by = acknowledged_by
            alarm.acknowledged_at = datetime.now(UTC)
            await session.flush()
        return alarm
