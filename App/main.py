from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Path
from models import Movies
import models
from database import SessionLocal, engine
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]


class MovieRequest(BaseModel):
    title: str = Field(min_length=4, max_length=20)
    description: str = Field(min_length=4, max_length=200)
    rating: int = Field(gt=0, lt=11)
    watched: bool


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dep):
    return db.query(models.Movies).all()


@app.get("/movie/{movie_id}", status_code=status.HTTP_200_OK)
async def read_movie(db: db_dep, movie_id: int = Path(gt=0)):
    movie_model = db.query(Movies).filter(Movies.id == movie_id).first()
    if movie_model is not None:
        return movie_model
    raise HTTPException(status_code=404, detail="Movie Not Found")


@app.post("/movie", status_code=status.HTTP_201_CREATED)
async def create_movie(db: db_dep, movie_request: MovieRequest):
    movie_model = Movies(**movie_request.model_dump())

    db.add(movie_model)
    db.commit()


@app.put("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_movie(
    db: db_dep, movie_request: MovieRequest, movie_id: int = Path(gt=0)
):
    movie_model = db.query(Movies).filter(Movies.id == movie_id).first()
    if movie_model is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    movie_model.title = movie_request.title
    movie_model.description = movie_request.description
    movie_model.rating = movie_request.rating
    movie_model.watched = movie_request.watched

    db.add(movie_model)
    db.commit()


@app.delete("/movie/{movie_id}")
async def delete_movie(db: db_dep, movie_id: int = Path(gt=0)):
    movie_model = db.query(Movies).filter(Movies.id == movie_id).first()
    if movie_model is None:
        HTTPException(status_code=404, detail="Movie Not Found")
    db.query(Movies).filter(Movies.id == movie_id).delete()

    db.commit()
