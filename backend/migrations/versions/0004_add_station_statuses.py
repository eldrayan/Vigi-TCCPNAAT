"""
Descrição: Adiciona o estado operacional atual das estações.
Autor: Leôncio Ferreira
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "station_statuses",
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("connection", sa.String(length=20), nullable=False),
        sa.Column("camera", sa.String(length=20), nullable=False),
        sa.Column("processing", sa.String(length=20), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("station_id"),
    )


def downgrade() -> None:
    op.drop_table("station_statuses")
