"""
Descrição: Mapeia a entidade de inspeção para a tabela do banco de dados.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Inspection(Base):
    __tablename__ = "inspections"
    __table_args__ = (
        CheckConstraint(
            "result IN ('CONFORME', 'NAO_CONFORME')",
            name="ck_inspections_result",
        ),
        CheckConstraint(
            "category IS NULL OR category IN "
            "('ANOMALIA_PRODUTO', 'FALHA_TECNICA')",
            name="ck_inspections_category",
        ),
        CheckConstraint(
            "nonconformity_type IS NULL OR nonconformity_type IN "
            "('SEM_TAMPA', 'TAMPA_TORTA', 'AMASSADO')",
            name="ck_inspections_nonconformity_type",
        ),
        CheckConstraint(
            "technical_failure_type IS NULL OR technical_failure_type IN "
            "('ERRO_CAPTURA', 'BAIXA_CONFIANCA', 'ERRO_INFERENCIA')",
            name="ck_inspections_technical_failure_type",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_inspections_confidence",
        ),
        CheckConstraint(
            "processing_time_ms >= 0",
            name="ck_inspections_processing_time",
        ),
        CheckConstraint(
            "(result = 'CONFORME' AND category IS NULL "
            "AND nonconformity_type IS NULL AND technical_failure_type IS NULL) "
            "OR (result = 'NAO_CONFORME' AND "
            "((category = 'ANOMALIA_PRODUTO' "
            "AND nonconformity_type IS NOT NULL "
            "AND technical_failure_type IS NULL) "
            "OR (category = 'FALHA_TECNICA' "
            "AND nonconformity_type IS NULL "
            "AND technical_failure_type IS NOT NULL)))",
            name="ck_inspections_classification",
        ),
        Index("idx_inspections_timestamp", "timestamp"),
        Index("idx_inspections_result", "result"),
        Index(
            "idx_inspections_nonconformity_type",
            "nonconformity_type",
        ),
    )

    inspection_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    result: Mapped[str] = mapped_column(String(20))
    category: Mapped[str | None] = mapped_column(String(30))
    nonconformity_type: Mapped[str | None] = mapped_column(String(30))
    technical_failure_type: Mapped[str | None] = mapped_column(String(30))
    confidence: Mapped[float | None] = mapped_column(Float)
    processing_time_ms: Mapped[float] = mapped_column(Float)
    model_format: Mapped[str] = mapped_column(String(30))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
    )
