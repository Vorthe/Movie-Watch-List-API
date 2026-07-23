"""create genre for Movies column

Revision ID: d9bb0f27d162
Revises: 5442f2589796
Create Date: 2026-07-23 22:56:51.954099

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d9bb0f27d162"
down_revision: Union[str, Sequence[str], None] = "5442f2589796"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("genre", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("movies", "genre")
