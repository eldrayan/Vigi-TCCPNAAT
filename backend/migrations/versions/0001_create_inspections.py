"""
Descrição: Cria a tabela e os índices iniciais do módulo de inspeções.
Autor: Leôncio Ferreira
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inspecoes",
        sa.Column("id_inspecao", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resultado", sa.String(20), nullable=False),
        sa.Column("categoria", sa.String(30), nullable=True),
        sa.Column("tipo_nao_conformidade", sa.String(30), nullable=True),
        sa.Column("tipo_falha_tecnica", sa.String(30), nullable=True),
        sa.Column("confianca", sa.Float(), nullable=True),
        sa.Column("tempo_processamento_ms", sa.Integer(), nullable=False),
        sa.Column(
            "recebido_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "resultado IN ('CONFORME', 'NAO_CONFORME')",
            name="ck_inspecoes_resultado",
        ),
        sa.CheckConstraint(
            "categoria IS NULL OR categoria IN "
            "('ANOMALIA_PRODUTO', 'FALHA_TECNICA')",
            name="ck_inspecoes_categoria",
        ),
        sa.CheckConstraint(
            "tipo_nao_conformidade IS NULL OR tipo_nao_conformidade IN "
            "('SEM_TAMPA', 'TAMPA_TORTA', 'AMASSADO')",
            name="ck_inspecoes_tipo_nao_conformidade",
        ),
        sa.CheckConstraint(
            "tipo_falha_tecnica IS NULL OR tipo_falha_tecnica IN "
            "('ERRO_CAPTURA', 'BAIXA_CONFIANCA', 'ERRO_INFERENCIA')",
            name="ck_inspecoes_tipo_falha_tecnica",
        ),
        sa.CheckConstraint(
            "confianca IS NULL OR confianca BETWEEN 0 AND 1",
            name="ck_inspecoes_confianca",
        ),
        sa.CheckConstraint(
            "tempo_processamento_ms >= 0",
            name="ck_inspecoes_tempo_processamento",
        ),
        sa.CheckConstraint(
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
    )
    op.create_index("idx_inspecoes_timestamp", "inspecoes", ["timestamp"])
    op.create_index("idx_inspecoes_resultado", "inspecoes", ["resultado"])
    op.create_index(
        "idx_inspecoes_tipo_nao_conformidade",
        "inspecoes",
        ["tipo_nao_conformidade"],
    )


def downgrade() -> None:
    op.drop_index("idx_inspecoes_tipo_nao_conformidade", table_name="inspecoes")
    op.drop_index("idx_inspecoes_resultado", table_name="inspecoes")
    op.drop_index("idx_inspecoes_timestamp", table_name="inspecoes")
    op.drop_table("inspecoes")
