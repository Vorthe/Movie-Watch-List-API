from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, desc, func, not_
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Movie, UserMovieStatus
from .auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/")
async def get_recommendations(
    user: user_dep,
    db: db_dep,
    limit: int = Query(20, ge=1, le=50),
):
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = user.get("id")

    # Step 1: How many movies has this user rated?
    rated_count = (
        db.query(UserMovieStatus)
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.rating.isnot(None),
        )
        .count()
    )

    if rated_count < 3:
        return {
            "message": (
                f"Rate at least 3 movies to get recommendations. "
                f"You have {rated_count}."
            ),
            "rated_count": rated_count,
            "top_genres": [],
            "recommendations": [],
        }

    # Step 2: Top 3 genres from high ratings (7+)
    top_genres_rows = (
        db.query(
            Movie.genre,
            func.avg(UserMovieStatus.rating).label("avg_rating"),
        )
        .join(UserMovieStatus, UserMovieStatus.movie_id == Movie.id)
        .filter(
            UserMovieStatus.user_id == user_id,
            UserMovieStatus.rating.isnot(None),
            UserMovieStatus.rating >= 7,
        )
        .group_by(Movie.genre)
        .order_by(desc("avg_rating"))
        .limit(3)
        .all()
    )

    top_genres = [g.genre for g in top_genres_rows]

    if not top_genres:
        return {
            "message": ("Rate a few movies with 7 or higher to get recommendations."),
            "rated_count": rated_count,
            "top_genres": [],
            "recommendations": [],
        }

    # Step 3: Movies in those genres the user has not touched yet
    touched_movie_ids = (
        db.query(UserMovieStatus.movie_id)
        .filter(UserMovieStatus.user_id == user_id)
        .subquery()
    )

    recs = (
        db.query(Movie)
        .filter(
            Movie.genre.in_(top_genres),
            not_(Movie.id.in_(touched_movie_ids)),
            Movie.external_rating.isnot(None),
        )
        .order_by(desc(Movie.external_rating))
        .limit(limit)
        .all()
    )

    return {
        "message": None,
        "rated_count": rated_count,
        "top_genres": top_genres,
        "recommendations": [
            {
                "id": m.id,
                "title": m.title,
                "genre": m.genre,
                "external_rating": (
                    float(m.external_rating) if m.external_rating else None
                ),
                "description": m.description,
            }
            for m in recs
        ],
    }
