"""
Admin panel setup using fastapi-admin-kit.

Creates a separate async engine (asyncpg) and mounts the admin panel.
Business models are registered for management.
Admin users live in the `admin_users` table (separate from our `users`).
"""

import os

from dotenv import load_dotenv

load_dotenv()  # Load .env FIRST, before reading any env var
# --- Dev only: disable CSRF ---


import os as _os

if _os.getenv("CSRF_ENABLED", "true").lower() == "false":
    from starlette.middleware.base import BaseHTTPMiddleware

    class _NoCSRFMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    # Monkey-patch both possible names
    import fastapi_admin_kit.auth.csrf as _csrf

    if hasattr(_csrf, "CSRFMiddleware"):
        _csrf.CSRFMiddleware = _NoCSRFMiddleware
    if hasattr(_csrf, "CSRFMiddlewareBase"):
        _csrf.CSRFMiddlewareBase = _NoCSRFMiddleware


from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_admin_kit import Admin
from fastapi_admin_kit.auth.backend import BuiltinAuthBackend
from fastapi_admin_kit.migrations.models import User as AdminUser
from fastapi_admin_kit.models.base import Base as AdminBase

from .models import Movie, Notification, UserMovieStatus, WatchSchedule

# Read raw env var (before database.py rewrites it)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Build async URL (asyncpg driver)
_async_db_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
_async_db_url = _async_db_url.replace("?sslmode=require", "")

_connect_args = {}
if os.getenv("DB_REQUIRE_SSL", "false").lower() == "true":
    _connect_args["ssl"] = "require"

async_engine = create_async_engine(
    _async_db_url,
    echo=False,
    connect_args=_connect_args,
)

# session_secure=False for localhost HTTP; True on HTTPS (Render)
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
)


# Register business models
admin.register(Movie)
admin.register(UserMovieStatus)
admin.register(Notification)
admin.register(WatchSchedule)
