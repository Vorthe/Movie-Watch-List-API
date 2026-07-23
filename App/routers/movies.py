from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Movies
from database import SessionLocal
from starlette import status
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


class MovieRequest(BaseModel):
    title: str = Field(min_length=4, max_length=20)
    description: str = Field(min_length=4, max_length=200)
    rating: int = Field(gt=0, lt=11)
    watched: bool
    genre: str = Field(min_length=4, max_length=20)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = db.query(Movies).filter(Movies.owner_id == user.get("id")).all()
    return movie_model


@router.get("/movie/{movie_id}", status_code=status.HTTP_200_OK)
async def read_movie(user: user_dep, db: db_dep, movie_id: int = Path(gt=0)):
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is not None:
        return movie_model
    raise HTTPException(status_code=404, detail="Movie Not Found")


@router.post("/movie", status_code=status.HTTP_201_CREATED)
async def create_movie(user: user_dep, db: db_dep, movie_request: MovieRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = Movies(**movie_request.model_dump(), owner_id=user.get("id"))

    db.add(movie_model)
    db.commit()


@router.put("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_movie(
    user: user_dep, db: db_dep, movie_request: MovieRequest, movie_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    movie_model.title = movie_request.title
    movie_model.description = movie_request.description
    movie_model.rating = movie_request.rating
    movie_model.watched = movie_request.watched

    db.add(movie_model)
    db.commit()


@router.delete("/movie/{movie_id}")
async def delete_movie(user: user_dep, db: db_dep, movie_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is None:
        HTTPException(status_code=404, detail="Movie Not Found")
    db.query(Movies).filter(Movies.id == movie_id).filter(
        Movies.owner_id == user.get("id")
    ).delete()

    db.commit()
