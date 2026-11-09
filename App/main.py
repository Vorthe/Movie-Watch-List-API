import os
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, movies, admin, users, notifications, schedule
from .models import Base
from .database import engine

app = FastAPI()

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
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(schedule.router)
