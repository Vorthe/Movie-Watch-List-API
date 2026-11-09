from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Movie, WatchSchedule
from .auth import get_current_user

router = APIRouter(prefix="/schedule", tags=["schedule"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


VALID_STATUSES = {"pending", "done", "missed"}


class ScheduleCreateRequest(BaseModel):
    movie_id: int = Field(gt=0)
    scheduled_date: date


class ScheduleUpdateRequest(BaseModel):
    status: str = Field(pattern="^(pending|done|missed)$")


class MovieInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    genre: str


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    movie_id: int
    scheduled_date: date
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    movie: MovieInfo


@router.post("/", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    user: user_dep,
    db: db_dep,
    payload: ScheduleCreateRequest,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    movie = db.query(Movie).filter(Movie.id == payload.movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")

    existing = (
        db.query(WatchSchedule)
        .filter(
            WatchSchedule.user_id == user.get("id"),
            WatchSchedule.movie_id == payload.movie_id,
            WatchSchedule.scheduled_date == payload.scheduled_date,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already scheduled for this date",
        )

    schedule = WatchSchedule(
        user_id=user.get("id"),
        movie_id=payload.movie_id,
        scheduled_date=payload.scheduled_date,
        status="pending",
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/", response_model=list[ScheduleResponse])
async def list_schedules(
    user: user_dep,
    db: db_dep,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    from_date: Optional[date] = Query(default=None),
    to_date: Optional[date] = Query(default=None),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = db.query(WatchSchedule).filter(WatchSchedule.user_id == user.get("id"))

    if status_filter:
        if status_filter not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid status filter")
        query = query.filter(WatchSchedule.status == status_filter)

    if from_date:
        query = query.filter(WatchSchedule.scheduled_date >= from_date)
    if to_date:
        query = query.filter(WatchSchedule.scheduled_date <= to_date)

    return query.order_by(WatchSchedule.scheduled_date.asc()).all()


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    user: user_dep,
    db: db_dep,
    payload: ScheduleUpdateRequest,
    schedule_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    schedule = (
        db.query(WatchSchedule)
        .filter(
            WatchSchedule.id == schedule_id,
            WatchSchedule.user_id == user.get("id"),
        )
        .first()
    )
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule Not Found")

    schedule.status = payload.status
    if payload.status == "done":
        schedule.completed_at = datetime.utcnow()
    else:
        schedule.completed_at = None

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    user: user_dep,
    db: db_dep,
    schedule_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    schedule = (
        db.query(WatchSchedule)
        .filter(
            WatchSchedule.id == schedule_id,
            WatchSchedule.user_id == user.get("id"),
        )
        .first()
    )
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule Not Found")

    db.delete(schedule)
    db.commit()
