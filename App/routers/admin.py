from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Movies
from ..database import SessionLocal
from starlette import status
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


@router.get("/movie", status_code=status.HTTP_200_OK)
async def read_all(user: user_dep, db: db_dep):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Movies).all()


@router.delete("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(user: user_dep, db: db_dep, movie_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = db.query(Movies).filter(Movies.id == movie_id).first()
    if movie_model is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    db.query(Movies).filter(Movies.id == movie_id).delete()
    db.commit()
