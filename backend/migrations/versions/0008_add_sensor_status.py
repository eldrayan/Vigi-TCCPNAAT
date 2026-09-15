"""Adiciona o estado do sensor à telemetria das estações.

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("station_statuses") as batch_op:
        batch_op.add_column(
            sa.Column(
                "sensor",
                sa.String(length=20),
                nullable=False,
                server_default="OFFLINE",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("station_statuses") as batch_op:
        batch_op.drop_column("sensor")
