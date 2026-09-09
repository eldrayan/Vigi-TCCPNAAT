"""
Descrição: Mapeia a entidade de inspeção para a tabela do banco de dados.
Autor: Leôncio Ferreira
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class Inspection(Base):
    __tablename__ = "inspecoes"
    __table_args__ = (
        CheckConstraint(
            "resultado IN ('CONFORME', 'NAO_CONFORME')",
            name="ck_inspecoes_resultado",
        ),
        CheckConstraint(
            "categoria IS NULL OR categoria IN "
            "('ANOMALIA_PRODUTO', 'FALHA_TECNICA')",
            name="ck_inspecoes_categoria",
        ),
        CheckConstraint(
            "tipo_nao_conformidade IS NULL OR tipo_nao_conformidade IN "
            "('SEM_TAMPA', 'TAMPA_TORTA', 'AMASSADO')",
            name="ck_inspecoes_tipo_nao_conformidade",
        ),
        CheckConstraint(
            "tipo_falha_tecnica IS NULL OR tipo_falha_tecnica IN "
            "('ERRO_CAPTURA', 'BAIXA_CONFIANCA', 'ERRO_INFERENCIA')",
            name="ck_inspecoes_tipo_falha_tecnica",
        ),
        CheckConstraint(
            "confianca IS NULL OR confianca BETWEEN 0 AND 1",
            name="ck_inspecoes_confianca",
        ),
        CheckConstraint(
            "tempo_processamento_ms >= 0",
            name="ck_inspecoes_tempo_processamento",
        ),
        CheckConstraint(
            "(resultado = 'CONFORME' AND categoria IS NULL "
            "AND tipo_nao_conformidade IS NULL AND tipo_falha_tecnica IS NULL) "
            "OR (resultado = 'NAO_CONFORME' AND "
            "((categoria = 'ANOMALIA_PRODUTO' "
            "AND tipo_nao_conformidade IS NOT NULL "
            "AND tipo_falha_tecnica IS NULL) "
            "OR (categoria = 'FALHA_TECNICA' "
            "AND tipo_nao_conformidade IS NULL "
            "AND tipo_falha_tecnica IS NOT NULL)))",
            name="ck_inspecoes_classificacao",
        ),
        Index("idx_inspecoes_timestamp", "timestamp"),
        Index("idx_inspecoes_resultado", "resultado"),
        Index(
            "idx_inspecoes_tipo_nao_conformidade",
            "tipo_nao_conformidade",
        ),
    )

    id_inspecao: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resultado: Mapped[str] = mapped_column(String(20))
    categoria: Mapped[str | None] = mapped_column(String(30))
    tipo_nao_conformidade: Mapped[str | None] = mapped_column(String(30))
    tipo_falha_tecnica: Mapped[str | None] = mapped_column(String(30))
    confianca: Mapped[float | None] = mapped_column(Float)
    tempo_processamento_ms: Mapped[int] = mapped_column(Integer)
    recebido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
    )
