from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from .routers import auth, movies, admin, users
from .models import Base
from .database import engine
from fastapi.staticfiles import StaticFiles

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="App/static"), name="static")


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
