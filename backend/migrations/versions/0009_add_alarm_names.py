"""Adiciona nomes às regras e aos eventos de alarme.

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("batches") as batch_op:
        batch_op.add_column(sa.Column("alarm_name", sa.String(length=100)))
    with op.batch_alter_table("alarms") as batch_op:
        batch_op.add_column(
            sa.Column(
                "name",
                sa.String(length=100),
                nullable=False,
                server_default="Alarme de qualidade",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("alarms") as batch_op:
        batch_op.drop_column("name")
    with op.batch_alter_table("batches") as batch_op:
        batch_op.drop_column("alarm_name")
