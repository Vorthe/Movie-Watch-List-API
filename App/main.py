from fastapi import FastAPI
from routers import auth, movies, admin, users
import models
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(admin.router)
app.include_router(users.router)
