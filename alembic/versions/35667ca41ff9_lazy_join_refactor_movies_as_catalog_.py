"""lazy join refactor: movies as catalog, user_movie_status

Revision ID: 35667ca41ff9
Revises: 6a25a64b6402
Create Date: 2026-11-04

Refactor: Movies become a shared catalog (no owner_id, no watched/rating).
Per-user state moves to user_movie_status. Existing user data is preserved.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "35667ca41ff9"
down_revision: Union[str, None] = "6a25a64b6402"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create user_movie_status table
    op.create_table(
        "user_movie_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("watched", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),
    )
    op.create_index("ix_user_movie_status_user_id", "user_movie_status", ["user_id"])
    op.create_index("ix_user_movie_status_movie_id", "user_movie_status", ["movie_id"])

    # 2. Migrate existing per-user data into the new table
    op.execute("""
        INSERT INTO user_movie_status
            (user_id, movie_id, watched, rating, created_at, updated_at)
        SELECT
            owner_id,
            id,
            COALESCE(watched, false),
            rating,
            NOW(),
            NOW()
        FROM movies
        WHERE owner_id IS NOT NULL
        """)

    # 3. Truncate any existing values that exceed new column limits
    op.execute("UPDATE movies SET title = LEFT(title, 200) WHERE LENGTH(title) > 200")
    op.execute(
        "UPDATE movies SET description = LEFT(description, 200) "
        "WHERE LENGTH(description) > 200"
    )
    op.execute("UPDATE movies SET genre = LEFT(genre, 50) WHERE LENGTH(genre) > 50")

    # 4. Enforce column length limits
    op.alter_column(
        "movies",
        "title",
        type_=sa.String(200),
        existing_type=sa.String(),
        existing_nullable=True,
    )
    op.alter_column(
        "movies",
        "description",
        type_=sa.String(200),
        existing_type=sa.String(),
        existing_nullable=True,
    )
    op.alter_column(
        "movies",
        "genre",
        type_=sa.String(50),
        existing_type=sa.String(),
        existing_nullable=True,
    )

    # 5. Add new catalog columns
    op.add_column(
        "movies",
        sa.Column("external_rating", sa.Numeric(3, 1), nullable=True),
    )
    op.add_column(
        "movies",
        sa.Column("external_id", sa.String(50), nullable=True),
    )
    op.add_column(
        "movies",
        sa.Column("external_source", sa.String(20), nullable=True),
    )
    op.add_column(
        "movies",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_movie_external", "movies", ["external_source", "external_id"]
    )

    # 6. Drop per-user columns from movies
    op.drop_constraint("movies_owner_id_fkey", "movies", type_="foreignkey")
    op.drop_column("movies", "owner_id")
    op.drop_column("movies", "watched")
    op.drop_column("movies", "rating")


def downgrade() -> None:
    # Restore per-user columns (data is lost, schema only)
    op.add_column("movies", sa.Column("rating", sa.Integer(), nullable=True))
    op.add_column("movies", sa.Column("watched", sa.Boolean(), nullable=True))
    op.add_column("movies", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "movies_owner_id_fkey", "movies", "users", ["owner_id"], ["id"]
    )

    op.drop_constraint("uq_movie_external", "movies", type_="unique")
    op.drop_column("movies", "created_at")
    op.drop_column("movies", "external_source")
    op.drop_column("movies", "external_id")
    op.drop_column("movies", "external_rating")
