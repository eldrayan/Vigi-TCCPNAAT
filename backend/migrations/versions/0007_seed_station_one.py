"""Cria a estação única padrão do protótipo Vigi.

Revision ID: 0007
Revises: 0006
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT OR IGNORE INTO stations (code, name, device_id)
        VALUES ('ESTACAO_01', 'Estação 01', 'ESTACAO_01')
        """
    )
    op.execute(
        """
        INSERT OR IGNORE INTO batches
        (code, station_id, status, started_at)
        SELECT 'LOTE_01', id, 'ATIVO', CURRENT_TIMESTAMP
        FROM stations WHERE code = 'ESTACAO_01'
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM batches WHERE code = 'LOTE_01' "
        "AND station_id = (SELECT id FROM stations WHERE code = 'ESTACAO_01')"
    )
    op.execute("DELETE FROM stations WHERE code = 'ESTACAO_01'")
