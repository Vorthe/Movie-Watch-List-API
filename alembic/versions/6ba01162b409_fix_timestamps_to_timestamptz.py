"""fix timestamps to timestamptz

Revision ID: 6ba01162b409
Revises: 844d74c9194c
Create Date: 2026-11-16 10:15:18.077627

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "6ba01162b409"
down_revision: Union[str, Sequence[str], None] = "844d74c9194c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE movies
            ALTER COLUMN created_at TYPE TIMESTAMPTZ
            USING created_at AT TIME ZONE 'UTC';
    """)
    op.execute("""
        ALTER TABLE user_movie_status
            ALTER COLUMN created_at TYPE TIMESTAMPTZ
                USING created_at AT TIME ZONE 'UTC',
            ALTER COLUMN updated_at TYPE TIMESTAMPTZ
                USING updated_at AT TIME ZONE 'UTC';
    """)
    op.execute("""
        ALTER TABLE notifications
            ALTER COLUMN created_at TYPE TIMESTAMPTZ
            USING created_at AT TIME ZONE 'UTC';
    """)
    op.execute("""
        ALTER TABLE watch_schedules
            ALTER COLUMN created_at TYPE TIMESTAMPTZ
                USING created_at AT TIME ZONE 'UTC',
            ALTER COLUMN completed_at TYPE TIMESTAMPTZ
                USING completed_at AT TIME ZONE 'UTC';
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE movies
            ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
    """)
    op.execute("""
        ALTER TABLE user_movie_status
            ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE,
            ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE;
    """)
    op.execute("""
        ALTER TABLE notifications
            ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE;
    """)
    op.execute("""
        ALTER TABLE watch_schedules
            ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE,
            ALTER COLUMN completed_at TYPE TIMESTAMP WITHOUT TIME ZONE;
    """)
