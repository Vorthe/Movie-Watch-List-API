"""fix admin user_id types to integer

Revision ID: fb7dafae72e6
Revises: 6ba01162b409
Create Date: ...

"""

from typing import Sequence, Union

from alembic import op

revision: str = "fb7dafae72e6"
down_revision: Union[str, Sequence[str], None] = "6ba01162b409"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Only run if the admin tables exist (created by fastapi-admin-kit).
    # If they don't exist yet, this migration is a no-op; the library
    # will create them later with its own schema.
    op.execute("""
        DO $$
        BEGIN
            -- admin_user_totp
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'admin_user_totp'
                  AND column_name = 'user_id'
                  AND data_type = 'character varying'
            ) THEN
                ALTER TABLE admin_user_totp
                    ALTER COLUMN user_id TYPE INTEGER USING user_id::integer;
            END IF;

            -- admin_refresh_tokens
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'admin_refresh_tokens'
                  AND column_name = 'user_id'
                  AND data_type = 'character varying'
            ) THEN
                ALTER TABLE admin_refresh_tokens
                    ALTER COLUMN user_id TYPE INTEGER USING user_id::integer;
            END IF;

            -- admin_user_permissions
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'admin_user_permissions'
                  AND column_name = 'user_id'
                  AND data_type = 'character varying'
            ) THEN
                ALTER TABLE admin_user_permissions
                    ALTER COLUMN user_id TYPE INTEGER USING user_id::integer;
            END IF;

            -- admin_notifications (library bug: wants varchar, DB has integer)
            -- We use our own `notifications` table, so we disable this one
            -- via enable_notification=False in admin_setup.py.
            -- This migration only fixes user_id IF it's varchar, which
            -- isn't the case in our current DB. Skip.
        END $$;
    """)


def downgrade() -> None:
    # No-op: we don't want to break the library's schema on rollback.
    pass
