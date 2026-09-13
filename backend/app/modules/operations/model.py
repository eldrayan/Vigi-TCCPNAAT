"""
Descrição: Mapeia estações, lotes e status para o banco de dados.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class StationStatus(Base):
    __tablename__ = "station_statuses"

    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True
    )
    connection: Mapped[str] = mapped_column(String(20), nullable=False)
    camera: Mapped[str] = mapped_column(String(20), nullable=False)
    processing: Mapped[str] = mapped_column(String(20), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("station_id", "code", name="uq_batches_station_code"),
        Index("idx_batches_station_status", "station_id", "status"),
        Index(
            "uq_batches_active_station",
            "station_id",
            unique=True,
            sqlite_where=text("status = 'ATIVO'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    max_nonconformity_rate: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
