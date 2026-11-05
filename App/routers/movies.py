from operator import or_
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from pytest import Session
from sqlalchemy import and_, desc, func, or_

from App.database import SessionLocal
from ..models import Movie, UserMovieStatus
from .auth import get_current_user

router = APIRouter(prefix="/movies", tags=["movies"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


# --- Response schemas ---


class UserStatusResponse(BaseModel):
    watched: bool
    rating: Optional[int] = None


class MovieWithStatus(BaseModel):
    id: int
    title: str
    description: str
    genre: str
    external_rating: Optional[float] = None
    user_status: Optional[UserStatusResponse] = None


class StatusUpdateRequest(BaseModel):
    watched: bool
    rating: Optional[int] = Field(default=None, ge=1, le=10)


# --- Routes ---
# NOTE: static paths (/stats, /group-by-genre) must be declared before
# dynamic paths (/{movie_id}). FastAPI matches routes in order, so a
# request to /movies/stats would otherwise be interpreted as /{movie_id}
# with movie_id="stats" and fail int conversion.


@router.get("/stats", status_code=200)
async def get_stats(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    total = db.query(Movie).count()

    watched = (
        db.query(UserMovieStatus)
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.watched.is_(True),
        )
        .count()
    )

    avg = (
        db.query(func.avg(UserMovieStatus.rating))
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.watched.is_(True),
            UserMovieStatus.rating.isnot(None),
        )
        .scalar()
    )

    return {
        "total_movies": total,
        "watched_movies": watched,
        "unwatched_movies": total - watched,
        "average_rating": round(float(avg), 2) if avg is not None else 0,
    }


@router.get("/group-by-genre", status_code=200)
async def group_by_genre(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    rows = (
        db.query(Movie.genre, func.count(UserMovieStatus.id))
        .outerjoin(
            UserMovieStatus,
            and_(
                UserMovieStatus.movie_id == Movie.id,
                UserMovieStatus.user_id == user_id,
                UserMovieStatus.watched.is_(True),
            ),
        )
        .group_by(Movie.genre)
        .order_by(Movie.genre)
        .all()
    )

    return [{"genre": g, "count": c} for g, c in rows]


@router.get("/", status_code=200, response_model=list[MovieWithStatus])
async def list_movies(
    user: user_dep,
    db: db_dep,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    watched: Optional[bool] = None,
    sort_by: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(48, ge=1, le=100),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    query = db.query(Movie, UserMovieStatus).outerjoin(
        UserMovieStatus,
        and_(
            UserMovieStatus.movie_id == Movie.id,
            UserMovieStatus.user_id == user_id,
        ),
    )

    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    if genre:
        query = query.filter(Movie.genre == genre)

    if watched is True:
        query = query.filter(UserMovieStatus.watched.is_(True))
    elif watched is False:
        query = query.filter(
            or_(
                UserMovieStatus.id.is_(None),
                UserMovieStatus.watched.is_(False),
            )
        )

    if sort_by == "title":
        query = query.order_by(Movie.title)
    elif sort_by == "rating":
        query = query.order_by(desc(func.coalesce(UserMovieStatus.rating, -1)))
    elif sort_by == "external_rating":
        query = query.order_by(desc(func.coalesce(Movie.external_rating, 0)))
    else:
        query = query.order_by(Movie.id)

    rows = query.offset(skip).limit(limit).all()

    result = []
    for movie, status in rows:
        result.append(
            MovieWithStatus(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                genre=movie.genre,
                external_rating=(
                    float(movie.external_rating)
                    if movie.external_rating is not None
                    else None
                ),
                user_status=(
                    UserStatusResponse(
                        watched=status.watched,
                        rating=status.rating,
                    )
                    if status is not None
                    else None
                ),
            )
        )
    return result


@router.get("/{movie_id}", status_code=200, response_model=MovieWithStatus)
async def get_movie(
    user: user_dep,
    db: db_dep,
    movie_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    row = (
        db.query(Movie, UserMovieStatus)
        .outerjoin(
            UserMovieStatus,
            and_(
                UserMovieStatus.movie_id == Movie.id,
                UserMovieStatus.user_id == user_id,
            ),
        )
        .filter(Movie.id == movie_id)
        .first()
    )

    if row is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")

    movie, status = row
    return MovieWithStatus(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        genre=movie.genre,
        external_rating=(
            float(movie.external_rating) if movie.external_rating is not None else None
        ),
        user_status=(
            UserStatusResponse(watched=status.watched, rating=status.rating)
            if status is not None
            else None
        ),
    )


@router.put("/{movie_id}/status", status_code=204)
async def upsert_status(
    user: user_dep,
    db: db_dep,
    request: StatusUpdateRequest,
    movie_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")

    status = (
        db.query(UserMovieStatus)
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.movie_id == movie_id,
        )
        .first()
    )

    if status is None:
        status = UserMovieStatus(
            user_id=user_id,
            movie_id=movie_id,
            watched=request.watched,
            rating=request.rating,
        )
        db.add(status)
    else:
        status.watched = request.watched
        status.rating = request.rating

    db.commit()


@router.delete("/{movie_id}/status", status_code=204)
async def delete_status(
    user: user_dep,
    db: db_dep,
    movie_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get("id")

    status = (
        db.query(UserMovieStatus)
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.movie_id == movie_id,
        )
        .first()
    )

    if status is not None:
        db.delete(status)
        db.commit()
    # Idempotent: returns 204 whether status existed or not.
