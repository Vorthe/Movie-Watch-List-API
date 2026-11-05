from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Movie
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


class MovieCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=200)
    genre: str = Field(min_length=1, max_length=50)
    external_rating: Optional[float] = Field(default=None, ge=0, le=10)
    external_id: Optional[str] = Field(default=None, max_length=50)
    external_source: Optional[str] = Field(default=None, max_length=20)


class MovieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    genre: str
    external_rating: Optional[float] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None


def _require_admin(user: dict) -> None:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


@router.get("/movies", response_model=list[MovieResponse])
async def list_catalog(
    user: user_dep,
    db: db_dep,
    skip: int = 0,
    limit: int = 100,
):
    _require_admin(user)
    return db.query(Movie).offset(skip).limit(limit).all()


@router.post("/movies", response_model=MovieResponse, status_code=201)
async def create_movie(
    user: user_dep,
    db: db_dep,
    payload: MovieCreateRequest,
):
    _require_admin(user)

    if payload.external_id and payload.external_source:
        exists = (
            db.query(Movie)
            .filter(
                Movie.external_id == payload.external_id,
                Movie.external_source == payload.external_source,
            )
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=400,
                detail="Movie with this external_id and source already exists",
            )

    movie = Movie(**payload.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@router.put("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    user: user_dep,
    db: db_dep,
    payload: MovieCreateRequest,
    movie_id: int = Path(gt=0),
):
    _require_admin(user)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")

    for field, value in payload.model_dump().items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/movies/{movie_id}", status_code=204)
async def delete_movie(
    user: user_dep,
    db: db_dep,
    movie_id: int = Path(gt=0),
):
    _require_admin(user)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")

    db.delete(movie)
    db.commit()
