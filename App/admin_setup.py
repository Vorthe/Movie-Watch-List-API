"""
Admin panel setup using fastapi-admin-kit.

Only initialized when DATABASE_URL points to PostgreSQL.
In test environments (SQLite), admin is None and all calls are no-ops.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
_is_postgres = DATABASE_URL.startswith("postgresql://")

if _is_postgres:
    from sqlalchemy.ext.asyncio import create_async_engine

    from fastapi_admin_kit import Admin, ModelAdmin
    from fastapi_admin_kit.auth.backend import BuiltinAuthBackend
    from fastapi_admin_kit.migrations.models import User as AdminUser
    from fastapi_admin_kit.models.base import Base as AdminBase

    from .models import (
        Movie,
        Notification,
        UserMovieStatus,
        WatchSchedule,
    )

    _async_db_url = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    ).replace("?sslmode=require", "")

    _connect_args = {}
    if os.getenv("DB_REQUIRE_SSL", "false").lower() == "true":
        _connect_args["ssl"] = "require"

    async_engine = create_async_engine(
        _async_db_url,
        echo=False,
        connect_args=_connect_args,
    )

    _session_secure = os.getenv("ADMIN_SESSION_SECURE", "false").lower() == "true"

    admin = Admin(
        engine=async_engine,
        base=AdminBase,
        auth_model=AdminUser,
        auth_backend=BuiltinAuthBackend(),
        secret_key="dev-fixed-admin-secret-key-at-least-32-chars-long-1234567890",
        title="Movie Watch List Admin",
        admin_path="/admin",
        session_secure=_session_secure,
        is_development=True,
        auto_discover=False,
        dashboard_stats=[],
        dashboard_charts=False,
        session_samesite="lax",
        enable_notification=False,
    )

    class MovieAdmin(ModelAdmin):
        ordering = ["id"]

    class UserMovieStatusAdmin(ModelAdmin):
        ordering = ["id"]

    class NotificationAdmin(ModelAdmin):
        ordering = ["id"]

    class WatchScheduleAdmin(ModelAdmin):
        ordering = ["id"]

    admin.register(Movie, MovieAdmin)
    admin.register(UserMovieStatus, UserMovieStatusAdmin)
    admin.register(Notification, NotificationAdmin)
    admin.register(WatchSchedule, WatchScheduleAdmin)
else:
    # Test / SQLite environment: skip admin entirely
    async_engine = None
    admin = None
