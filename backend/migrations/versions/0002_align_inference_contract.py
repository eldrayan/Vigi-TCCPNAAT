"""
Descrição: Alinha a persistência ao contrato de saída do modelo de inferência.
Autor: Leôncio Ferreira
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("inspections") as batch_op:
        batch_op.alter_column(
            "processing_time_ms",
            existing_type=sa.Integer(),
            type_=sa.Float(),
            existing_nullable=False,
        )
        batch_op.add_column(
            sa.Column(
                "model_format",
                sa.String(length=30),
                nullable=False,
                server_default="unknown",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("inspections") as batch_op:
        batch_op.drop_column("model_format")
        batch_op.alter_column(
            "processing_time_ms",
            existing_type=sa.Float(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
