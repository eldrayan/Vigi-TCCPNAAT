"""
Descrição: Adiciona estações, lotes e vínculos às inspeções.
Autor: Leôncio Ferreira
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("device_id"),
    )
    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "code", name="uq_batches_station_code"),
    )
    op.create_index("idx_batches_station_status", "batches", ["station_id", "status"])
    op.create_index(
        "uq_batches_active_station",
        "batches",
        ["station_id"],
        unique=True,
        sqlite_where=sa.text("status = 'ATIVO'"),
    )

    with op.batch_alter_table("inspections") as batch_op:
        batch_op.add_column(sa.Column("station_code", sa.String(length=50)))
        batch_op.add_column(sa.Column("batch_code", sa.String(length=100)))
        batch_op.add_column(sa.Column("station_id", sa.Integer()))
        batch_op.add_column(sa.Column("batch_id", sa.Integer()))
        batch_op.create_foreign_key(
            "fk_inspections_station_id",
            "stations",
            ["station_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_inspections_batch_id",
            "batches",
            ["batch_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    with op.batch_alter_table("inspections") as batch_op:
        batch_op.drop_constraint("fk_inspections_batch_id", type_="foreignkey")
        batch_op.drop_constraint("fk_inspections_station_id", type_="foreignkey")
        batch_op.drop_column("batch_id")
        batch_op.drop_column("station_id")
        batch_op.drop_column("batch_code")
        batch_op.drop_column("station_code")

    op.drop_index("uq_batches_active_station", table_name="batches")
    op.drop_index("idx_batches_station_status", table_name="batches")
    op.drop_table("batches")
    op.drop_table("stations")
