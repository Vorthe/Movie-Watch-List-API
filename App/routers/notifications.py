from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Notification
from .auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message: str
    read: bool
    created_at: datetime


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    user: user_dep,
    db: db_dep,
    unread_only: bool = False,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = db.query(Notification).filter(Notification.user_id == user.get("id"))
    if unread_only:
        query = query.filter(Notification.read.is_(False))

    return query.order_by(Notification.created_at.desc()).all()


@router.get("/unread-count")
async def get_unread_count(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.get("id"),
            Notification.read.is_(False),
        )
        .count()
    )
    return {"unread_count": count}


@router.patch("/{notification_id}/read", status_code=204)
async def mark_read(
    user: user_dep,
    db: db_dep,
    notification_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user.get("id"),
        )
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification Not Found")

    if not notification.read:
        notification.read = True
        db.commit()


@router.post("/read-all", status_code=204)
async def mark_all_read(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db.query(Notification).filter(
        Notification.user_id == user.get("id"),
        Notification.read.is_(False),
    ).update({"read": True})
    db.commit()
