import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .admin_setup import admin, async_engine
from .database import engine
from .models import Base
from .routers import admin as admin_router
from .routers import auth, movies, notifications, schedule, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await admin.setup(app)

    # Dev only: strip CSRF middleware added by admin.setup()
    if os.getenv("CSRF_ENABLED", "true").lower() == "false":
        from fastapi_admin_kit.auth.csrf import CSRFMiddleware

        app.user_middleware = [
            m
            for m in app.user_middleware
            if getattr(m, "cls", None) is not CSRFMiddleware
            and getattr(m, "cls", None).__name__ != "CSRFMiddleware"
            and getattr(m, "cls", None).__name__ != "_NoCSRFMiddleware"
        ]

    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)


# Dev only: override CSRF dependency when CSRF_ENABLED=false
if os.getenv("CSRF_ENABLED", "true").lower() == "false":
    from fastapi_admin_kit.auth.csrf import require_csrf_token

    app.dependency_overrides[require_csrf_token] = lambda: True


cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/movies/movie-page", status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(admin_router.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(schedule.router)
