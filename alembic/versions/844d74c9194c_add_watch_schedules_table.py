"""add watch schedules table

Revision ID: 844d74c9194c
Revises: 0a190030854c
Create Date: 2026-11-09 10:36:32.906414

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "844d74c9194c"
down_revision: Union[str, Sequence[str], None] = "0a190030854c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "watch_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "movie_id", "scheduled_date", name="uq_user_movie_date"
        ),
    )
    op.create_index(
        op.f("ix_watch_schedules_movie_id"),
        "watch_schedules",
        ["movie_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watch_schedules_scheduled_date"),
        "watch_schedules",
        ["scheduled_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watch_schedules_status"),
        "watch_schedules",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watch_schedules_user_id"),
        "watch_schedules",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_watch_schedules_user_id"), table_name="watch_schedules")
    op.drop_index(op.f("ix_watch_schedules_status"), table_name="watch_schedules")
    op.drop_index(
        op.f("ix_watch_schedules_scheduled_date"), table_name="watch_schedules"
    )
    op.drop_index(op.f("ix_watch_schedules_movie_id"), table_name="watch_schedules")
    op.drop_table("watch_schedules")
