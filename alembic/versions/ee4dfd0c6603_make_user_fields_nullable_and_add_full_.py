"""make user fields nullable for simplified signup

Revision ID: ee4dfd0c6603
Revises: fb7dafae72e6
Create Date: ...

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "ee4dfd0c6603"
down_revision: Union[str, Sequence[str], None] = "fb7dafae72e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "username", nullable=True)
    op.alter_column("users", "first_name", nullable=True)
    op.alter_column("users", "last_name", nullable=True)
    op.alter_column("users", "phone_number", nullable=True)


def downgrade() -> None:
    op.alter_column("users", "username", nullable=False)
    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False)
    op.alter_column("users", "phone_number", nullable=False)
