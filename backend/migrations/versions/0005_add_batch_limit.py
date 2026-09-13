"""
Descrição: Adiciona o limite de não conformidade configurável por lote.
Autor: Leôncio Ferreira
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("batches") as batch_op:
        batch_op.add_column(sa.Column("max_nonconformity_rate", sa.Float()))


def downgrade() -> None:
    with op.batch_alter_table("batches") as batch_op:
        batch_op.drop_column("max_nonconformity_rate")
