"""
Descrição: Cria a tabela e os índices iniciais do módulo de inspeções.
Autor: Leôncio Ferreira
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inspections",
        sa.Column("inspection_id", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("category", sa.String(30), nullable=True),
        sa.Column("nonconformity_type", sa.String(30), nullable=True),
        sa.Column("technical_failure_type", sa.String(30), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "result IN ('CONFORME', 'NAO_CONFORME')",
            name="ck_inspections_result",
        ),
        sa.CheckConstraint(
            "category IS NULL OR category IN "
            "('ANOMALIA_PRODUTO', 'FALHA_TECNICA')",
            name="ck_inspections_category",
        ),
        sa.CheckConstraint(
            "nonconformity_type IS NULL OR nonconformity_type IN "
            "('SEM_TAMPA', 'TAMPA_TORTA', 'AMASSADO')",
            name="ck_inspections_nonconformity_type",
        ),
        sa.CheckConstraint(
            "technical_failure_type IS NULL OR technical_failure_type IN "
            "('ERRO_CAPTURA', 'BAIXA_CONFIANCA', 'ERRO_INFERENCIA')",
            name="ck_inspections_technical_failure_type",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_inspections_confidence",
        ),
        sa.CheckConstraint(
            "processing_time_ms >= 0",
            name="ck_inspections_processing_time",
        ),
        sa.CheckConstraint(
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
    )
    op.create_index("idx_inspections_timestamp", "inspections", ["timestamp"])
    op.create_index("idx_inspections_result", "inspections", ["result"])
    op.create_index(
        "idx_inspections_nonconformity_type",
        "inspections",
        ["nonconformity_type"],
    )


def downgrade() -> None:
    op.drop_index("idx_inspections_nonconformity_type", table_name="inspections")
    op.drop_index("idx_inspections_result", table_name="inspections")
    op.drop_index("idx_inspections_timestamp", table_name="inspections")
    op.drop_table("inspections")
